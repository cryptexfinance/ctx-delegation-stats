from sqlalchemy import desc

from .database import Session
from .graphql import DataCruncher
from .models import (
    DelegateChanged,
    DelegatorCreated,
    DelegateVotesChanged,
    Staked,
    Transfer,
    Withdrawn
)


def fetch_and_write_delegator_created():
    with Session() as session:
        last_delegator_created = session.query(DelegatorCreated).order_by(desc(DelegatorCreated.blockNumber)).first()

    if last_delegator_created:
        block_number = last_delegator_created.blockNumber
    else:
        block_number = 0

    DataCruncher(
        DelegatorCreated,
        "delegatorCreateds",
        ["id", "delegator", "delegatee", "blockNumber", "blockTimestamp", "transactionHash"],
        "blockNumber",
        block_number,
    ).fetch_and_write_to_db()


def fetch_and_write_delegator_changed():
    with Session() as session:
        last_delegator_changed = session.query(DelegateChanged).order_by(desc(DelegateChanged.blockNumber)).first()

    if last_delegator_changed:
        block_number = last_delegator_changed.blockNumber
    else:
        block_number = 0

    DataCruncher(
        DelegateChanged,
        "delegateChangeds",
        ["id", "delegator", "fromDelegate", "toDelegate", "blockNumber", "blockTimestamp", "transactionHash"],
        "blockNumber",
        block_number,
    ).fetch_and_write_to_db()


def fetch_and_write_delegate_votes_changed():
    with Session() as session:
        last_delegator_votes_changed = session.query(
            DelegateVotesChanged).order_by(desc(DelegateVotesChanged.blockNumber)).first()

    if last_delegator_votes_changed:
        block_number = last_delegator_votes_changed.blockNumber
    else:
        block_number = 0

    DataCruncher(
        DelegateVotesChanged,
        "delegateVotesChangeds",
        ["id", "delegate", "previousBalance", "newBalance", "blockNumber", "blockTimestamp", "transactionHash"],
        "blockNumber",
        block_number,
    ).fetch_and_write_to_db()


def fetch_and_write_staked():
    with Session() as session:
        last_staked = session.query(
            Staked).order_by(desc(Staked.blockNumber)).first()

    if last_staked:
        block_number = last_staked.blockNumber
    else:
        block_number = 0

    DataCruncher(
        Staked,
        "stakeds",
        ["id", "delegator", "delegatee", "amount", "blockNumber", "blockTimestamp", "transactionHash"],
        "blockNumber",
        block_number,
    ).fetch_and_write_to_db()


def fetch_and_write_transfer():
    with Session() as session:
        last_transfer = session.query(
            Transfer).order_by(desc(Transfer.blockNumber)).first()

    if last_transfer:
        block_number = last_transfer.blockNumber
    else:
        block_number = 0

    DataCruncher(
        Transfer,
        "transfers",
        ["id", "from", "to", "amount", "blockNumber", "blockTimestamp", "transactionHash"],
        "blockNumber",
        block_number,
        rename_fields={"from": "from_"},
    ).fetch_and_write_to_db()


def fetch_and_write_withdrawn():
    with Session() as session:
        last_transfer = session.query(
            Withdrawn).order_by(desc(Withdrawn.blockNumber)).first()

    if last_transfer:
        block_number = last_transfer.blockNumber
    else:
        block_number = 0

    DataCruncher(
        Withdrawn,
        "withdrawns",
        ["id", "delegator", "delegatee", "amount", "blockNumber", "blockTimestamp", "transactionHash"],
        "blockNumber",
        block_number,
    ).fetch_and_write_to_db()


def fetch_all_data():
    fetch_and_write_delegator_created()
    fetch_and_write_delegator_changed()
    fetch_and_write_delegate_votes_changed()
    fetch_and_write_staked()
    fetch_and_write_transfer()
    fetch_and_write_withdrawn()
