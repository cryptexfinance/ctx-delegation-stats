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

The formula for the distribution is explained using an example. 

Let’s say that `K1` voted on `n1` proposals and `k2` voted on `n2` proposals.

The reward for `K1 = (2 ** n1 * 0.2R)/(2 ** n1 + 2 ** n2)`

An exponential function is chosen here to reward active keepers more than non-active ones.

Similarly reward for `K2 = (2 ** n2 * 0.2R)/(2 ** n1 + 2 ** n2)`

To understand the user distribution, let’s an example.

Let's the user balance was as shown in the table at the time when each proposal was voted on.

| User | Delegated to | 	No of days | Amount staked | ProposalId |
|------|--------------|--------------|---------------|------------|
| U1	  | K1           | 	d1         | 	a1          | 1          |
| U1	  | K1           | 	d2         | 	a2          | 2          |
| U2	  | K1           | 	d3         | 	a3          | 1          |
| U2	  | K2           | 	d4         | 	a4          | 1          |
| U3	  | K3           | 	d5         | 	a5          | 2          |


Also, let's say the table for the keeper votes looks as follows:

| Keeper | proposalId |
|--------|------------|
| k1     | 1          |
| k1     | 2          |
| K2     | 1          |
| k3     | 2          |


We can see that K1 voted on 2 proposals, K2 voted n 1, K3 voted on 1 and K4 didn't vote on any proposals.

We first need to calculate rewards for each of keepers delegators. 
The reward pool for each keeper will be calculated as
User reward pool for K1 `UrK1 = (2 **2 * 0.8R)/(2**2 + 2**1 + 2**1)`
User reward pool for K2 `UrK2 = (2 **1 * 0.8R)/(2**2 + 2**1 + 2**1)`
User reward pool for K3 `UrK3 = (2 **1 * 0.8R)/(2**2 + 2**1 + 2**1)`
User reward pool for K4 `UrK4 = 0`

We further divide the keeper rewards for each proposal based on the number of proposals the keeper voted on
K1 User reward pool for proposalId 1 `UrK1P1 = UrK1 / 2`
K1 User reward pool for proposalId 2 `UrK1P2 = UrK1 / 2`
K2 User reward pool for proposalId 1 `UrK2P1 = UrK2`
K2 User reward pool for proposalId 2 `UrK2P2 = 0`
K3 User reward pool for proposalId 1 `UrK3P1 = 0`
K3 User reward pool for proposalId 2 `UrK3P2 = UrK3`
K4 User reward pool for proposalId 1 `UrK4P1 = 0`
K4 User reward pool for proposalId 2 `UrK4P2 = 0`

Reward for U1 for proposal 1  for delegating to keeper 1:`U1K1P1 = (d1 * a1 * UrK1P1) / (d1 * a1 + d3 * a3)`
Reward for U2 for proposal 1  for delegating to keeper 1: `U2K1P1 = (d3 * a3 * UrK1P1) / (d1 * a1 + d3 * a3)`
Reward for U2 for proposal 1  for delegating to keeper 2: `U2K2P1 = (d3 * a3 * UrK2P1) / (d1 * a1 + d3 * a3)`
Reward for U3 for proposal 1  for delegating to keeper 3: `U3K3P1 = 0`

Please note that U2 has been rewarded twice becasue they had delegated to 2 keepers during proposal 1 

Reward for U1 for proposal 2  for delegating to keeper 1 `U1K1P2 = (d1 * a1 * UrK1P2) / (d1 * a1)`
Reward for U3 for proposal 2  for delegating to keeper 3 `U3K3P2 = (d5 * a5 * UrK3P2) / (d1 * a1)`


Total reward for U1 `TU1 = U1K1P1 + U1K1P2`
Total reward for U2 `TU2 = U2K1P1 + U2K2P1`
Total reward for U3 `TU2 = U3K3P2`
