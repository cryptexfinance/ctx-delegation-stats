from setuptools import (
    setup,
)


setup(
    name="ctx_delegation_stats",
    version="0.0.1",
    description="""ctx delegation stats""",
    long_description_content_type="text/markdown",
    author="Cryptex Finance",
    author_email="voith@cryptex.finance",
    include_package_data=True,
    install_requires=[
        "click>=8.1.7",
        "eth-hash[pycryptodome]>=0.6.0,<0.7.0",
        "eth-utils>=3.0.0,<4.0.0",
        "pandas>=2.1.4",
        "python-dotenv>=1.0.0",
        "psycopg2>=2.9.9",
        "requests>=2.31.0",
        "SQLAlchemy>=2.0.25",
        "XlsxWriter>=3.1.9",
    ],
    python_requires=">=3.11.0",
    license="MIT",
    zip_safe=False,
    keywords="DeFi",
)
