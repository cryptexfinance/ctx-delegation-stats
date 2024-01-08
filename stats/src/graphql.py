import time
import json
from collections import defaultdict

import requests

from .config import GRAPH_QUERY_URL
from .database import Session
from .utils import identity

QUERY = """
{{
  {table_key} ( first: {first}, orderBy: {page_key} , where: {{ {page_key}_gt: "{page_value}" }} ) {{
    {fields}
  }}
}}
"""


class GraphQueryHandler:

    def __init__(self, table_key, fields, page_key, page_value, page_size=1000, url=None):
        if url is None:
            self.url = GRAPH_QUERY_URL
        else:
            self.url = url
        self.table_key = table_key
        self.page_key = page_key
        self.page_value = page_value
        self.fields = fields
        self.page_size = page_size

    def fetch_results(self):
        page_value = self.page_value
        results_len = self.page_size
        while results_len == self.page_size:
            query = QUERY.format(
                table_key=self.table_key,
                first=self.page_size,
                page_key=self.page_key,
                page_value=page_value,
                fields='\n'.join(self.fields)
            )
            # https://stackoverflow.com/questions/52051989/requests-exceptions-connectionerror-connection-aborted-connectionreseterro
            time.sleep(0.01)
            response = self._make_request(query)
            try:
                results = response["data"][self.table_key]
            except KeyError:
                raise Exception(response)

            yield results
            page_value = results[-1][self.page_key] if results else 0
            results_len = len(results)

    def _make_request(self, query):
        response = requests.post(
            self.url,
            data=json.dumps({"query": query}),
            headers={
               "Content-Type": "application/json"
            }
        )
        response.raise_for_status()
        return response.json()


class DataCruncher:
    transformers = defaultdict(lambda: identity)

    def __init__(
            self,
            model,
            table_key,
            fields,
            page_key,
            page_value,
            ignore_if_exists=list(),
            add_fields=dict(),
            transformers=dict(),
            rename_fields=dict(),
            url=None
    ):
        self.model = model
        self.transformers.update(transformers)
        self.rename_fields = rename_fields
        self.add_fields = add_fields
        self.ignore_if_exists = ignore_if_exists
        self.query_handler = GraphQueryHandler(
            table_key, fields, page_key, page_value, url=url
        )

    def fetch_and_write_to_db(self):
        for results in self.query_handler.fetch_results():
            for result in results:
                transformed_data = self._transform_data(result)
                data = self._add_fields(transformed_data)
                renamed_data = self._rename_fields(data)
                if self._ignore_if_exists(renamed_data):
                    continue
                with Session() as session:
                    instance = self.model(**renamed_data)
                    session.add(instance)
                    session.commit()

    def _ignore_if_exists(self, data):
        if not self.ignore_if_exists:
            return
        with Session() as session:
            result = session.query(self.model).filter_by(**{key: data[key] for key in self.ignore_if_exists}).first()
        return result is not None

    def _rename_fields(self, data):
        new_dict = dict()
        for key in data:
            if key in self.rename_fields:
                new_dict[self.rename_fields[key]] = data[key]
            else:
                new_dict[key] = data[key]
        return new_dict

    def _transform_data(self, data):
        return dict(
            map(lambda key: (key, self.transformers[key](data[key])), data)
        )

    def _add_fields(self, data):
        return data | self.add_fields
