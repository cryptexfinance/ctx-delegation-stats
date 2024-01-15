## CTX Delegation Rewards Generator

This repository contains code to calculate rewards discussed in this [proposal](https://forum.cryptex.finance/t/ctx-retroactive-airdrop-distribution-process/398).


#### Setup
1. Create a database in postgres
create a database named `ctx_delegation_stats` in postgres
```
CREATE DATABASE ctx_delegation_stats;
```
2. clone the repo
```bash
 git clone https://github.com/cryptexfinance/ctx-delegation-stats.git
```

3. Change directory to get access to the python scripts
```
 cd ctx-delegation-stats/stats
```

4. Setup env variables
create a .env from the existing `env.sample` file
```
cp env.sample .env
```
set the `DATABASE_URL`. Please refer to the sqlalchemy [docs](https://docs.sqlalchemy.org/en/20/core/engines.html) for more details.

5. Install python packages
In a python virtual env install the python libraries by running: 
```
pip install -e .
```
 6. Create the database models
```
python run.py create-models
```
 
7. To fetch all delegation data from the subgraph, run
```
python run.py fetch-and-store-data
```

### Generate Distribution
 Please make sure that you complete all the steps in setup before generating the excel sheet for the distribution. 
 
To generate the excel sheet for the distribution run:
```
python run.py generate-distribution
```
 This will generate a file named `distribution_data.xlsx` in the current working directory. 
 
Here's a link to the excel sheet generated using this code: [link](https://docs.google.com/spreadsheets/d/1A6F0IhLPDSx-rOGQi5q-Gtitn0Lyq2HRgfnEK1Cvl4c/edit?usp=sharing)  

### Distribution procedure

The code for the distribution process can be found [here](./stats/src/stats.py)

### Distribution Math

Formula
Let’s say there are 2 keepers `K1` and `K2` and 5 users `U1`, `U2`, `U3`, `U4`, `U5`.

Let’s say the total reward pool is `R`.

We will allocate 20% of the rewards i.e. `0.2R` to the keepers as rewards and 80% to the users i.e. `0.8R`.

Note: The numbers above can be changed based on feedback. Those are tentative numbers.

Let’s say that `K1` voted on `n1` proposals and `k2` voted on `n2` proposals.

The reward for `K1 = (2 ** n1 * 0.2R)/(2 ** n1 + 2 ** n2)`

An exponential function is chosen here to reward active keepers more than non-active ones.

Similarly reward for `K2 = (2 ** n2 * 0.2R)/(2 ** n1 + 2 ** n2)`

User rewards distribution


|User|	Delegated to|	No of days|	Amount staked|
| -------- | ------- | ------- | ------- |
|U1	|K1|	d1|	a1|
|U2	|K1|	d2|	a2|
|U3	|K2|	d3|	a3|
|U4	|K3|	d4|	a4|
|U4	|K4|	d5|	a5|
Let’s say the users have the following distribution:

Firstly the reward pool for each keeper will be split based on the keeper’s participation.

user reward pool for `K1(UrK1) = (2 ** n1 * 0.8R) / (2 ** n1 + 2 ** n2)`
user reward pool for `K2(UrK2) = (2 ** n2 * 0.8R )/ (2 ** n1 + 2 ** n2)`

Reward for `U1 = (d1 * a1 * UrK1) / (d1 * a1 + d2 * a2)`
Reward for `U2 = (d2 * a2 * UrK1) / (d1 * a1 + d2 * a2)`

Reward for `U3 = (d3 * a3 * UrK2) / (d3 * a3 + d4 * a4 + d5 * a5)`
Reward for `U4 = (d4 * a4 * UrK2) / (d3 * a3 + d4 * a4 + d5 * a5)`
Reward for `U5 = (d5 * a5 * UrK2) / (d3 * a3 + d4 * a4 + d5 * a5)`

Based on this formula we will grab the information of stakers and will create a document with the details on how much CTX will be allocated per staker/delegator for the community to approve.