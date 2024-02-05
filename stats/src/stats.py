import datetime
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal

import pandas as pd
from eth_utils.address import to_checksum_address
from eth_utils.currency import from_wei
from sqlalchemy import and_, func

from .database import Session
from .models import (
    DelegateChanged,
    DelegateVotesChanged,
    Staked,
    Transfer,
    Withdrawn,
    DelegationRecord,
    EventType,
    VoteCast,
    VoteStat,
)


class DataExists:
    PRESENT = True
    ABSENT = False


@dataclass
class EventData:
    delegate_changed: DelegateChanged
    delegate_votes_changed: DelegateVotesChanged
    staked: Staked
    transfer: Transfer
    withdrawn: Withdrawn


class DelegatesChangedData(DataExists):
    ...


class DelegateVotesChangedData(DataExists):
    ...


class StakedData(DataExists):
    ...


class TransferData(DataExists):
    ...


class WithdrawnData(DataExists):
    ...


CTX_DELEGATION_CHECK = [
    DelegatesChangedData.PRESENT,
    DelegateVotesChangedData.PRESENT,
    StakedData.ABSENT,
    TransferData.ABSENT,
    WithdrawnData.ABSENT
]
STAKED_CHECK = [
    DelegatesChangedData.ABSENT,
    DelegateVotesChangedData.PRESENT,
    StakedData.PRESENT,
    TransferData.PRESENT,
    WithdrawnData.ABSENT
]
CTX_TRANSFER_CHECK = [
    DelegatesChangedData.ABSENT,
    DelegateVotesChangedData.PRESENT,
    StakedData.ABSENT,
    TransferData.PRESENT,
    WithdrawnData.ABSENT
]
WITHDRAWN_CHECK = [
    DelegatesChangedData.ABSENT,
    DelegateVotesChangedData.PRESENT,
    StakedData.ABSENT,
    TransferData.PRESENT,
    WithdrawnData.PRESENT
]
# CTX_DELEGATION_CHECK_1 = [
#     DelegatesChangedData,
#     DelegateVotesChangedData,
#     StakedData,
#     TransferData,
#     WithdrawnData
# ]

CRYPTEX_TEAM_MULTISIG_ADDRESS = '0xa70b638b70154edfcbb8dbbbd04900f328f32c35'


def convert_epoch_to_datetime(timestamp: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(timestamp)


def no_of_days(timestamp1: datetime.datetime, timestamp2: datetime.datetime) -> int:
    return (timestamp2 - timestamp1).days


START_BLOCK = 13360297
START_DATETIME = convert_epoch_to_datetime(1633453569)
END_BLOCK_TIMESTAMP = 1703980800

class BuildAccountDelegation:

    def build(self):
        with Session() as session:
            subquery = session.query(
                DelegateVotesChanged.blockNumber,
                DelegateVotesChanged.transactionHash,
                DelegateVotesChanged.blockTimestamp,
            ).distinct(DelegateVotesChanged.transactionHash).subquery()
            for delegate_vote_changed in session.query(
                    subquery.c.transactionHash, subquery.c.blockNumber, subquery.c.blockTimestamp
            ).order_by(subquery.c.blockNumber).all():
                event_type, data = self.classify_event_type(
                    session,
                    delegate_vote_changed.transactionHash
                )
                self.write_record(
                    session,
                    delegate_vote_changed.transactionHash,
                    delegate_vote_changed.blockNumber,
                    delegate_vote_changed.blockTimestamp,
                    event_type,
                    data
                )

    def write_record(self, session, tx_hash, block_number, block_timestamp, event_type, data):
        if event_type == EventType.DIRECT_DELEGATION:
            if len(data.delegate_changed) == 1 and len(data.delegate_votes_changed) == 1:
                # 0x9c7118eb0c347a84f1411060c580ee1fe354de4bc82f885ffea7e53970c5bf27
                latest_balance = self.get_latest_balance(
                    session,
                    data.delegate_changed[0].delegator,
                    data.delegate_changed[0].toDelegate
                )
                record = DelegationRecord(
                    delegator=data.delegate_changed[0].delegator,
                    delegatee=data.delegate_changed[0].toDelegate,
                    balance=latest_balance + data.delegate_votes_changed[0].newBalance - data.delegate_votes_changed[
                        0].previousBalance,
                    event_type=event_type,
                    blockNumber=block_number,
                    blockTimestamp=block_timestamp,
                    transactionHash=tx_hash
                )
                session.add(record)
            elif len(data.delegate_changed) == 1 and len(data.delegate_votes_changed) == 2 and \
                    data.delegate_votes_changed[0].newBalance == 0:
                # delegator changed; old delegator balance becomes 0, new one gets 1st event previousBalance.
                # Also for the 2nd event newBalance - oldBalance = previousBalance of 1st event
                # 0x0dc8bca57fbf2d4c283a1130e29d51c927a7cb93c0dcc297b157ea4936fe0fd3
                latest_balance2 = self.get_latest_balance(
                    session,
                    data.delegate_changed[0].delegator,
                    data.delegate_changed[0].fromDelegate
                )
                record1 = DelegationRecord(
                    delegator=data.delegate_changed[0].delegator,
                    delegatee=data.delegate_changed[0].fromDelegate,
                    balance=latest_balance2 + (data.delegate_votes_changed[0].newBalance - data.delegate_votes_changed[
                        0].previousBalance),
                    event_type=event_type,
                    blockNumber=block_number,
                    blockTimestamp=block_timestamp,
                    transactionHash=tx_hash
                )
                latest_balance2 = self.get_latest_balance(
                    session,
                    data.delegate_changed[0].delegator,
                    data.delegate_changed[0].toDelegate
                )
                record2 = DelegationRecord(
                    delegator=data.delegate_changed[0].delegator,
                    delegatee=data.delegate_changed[0].toDelegate,
                    balance=latest_balance2 + (data.delegate_votes_changed[1].newBalance - data.delegate_votes_changed[
                        1].previousBalance),
                    event_type=event_type,
                    blockNumber=block_number,
                    blockTimestamp=block_timestamp,
                    transactionHash=tx_hash
                )
                session.add(record1)
                session.add(record2)
            else:
                raise Exception('Unknown type')
        elif event_type == EventType.STAKED:
            if len(data.staked) == 1 and len(data.delegate_votes_changed) == 1:
                # 0xe6d954dc98bf0dcda580463aa1a01ba773943f2480c2780a596cf565622361e1
                latest_balance = self.get_latest_balance(
                    session,
                    data.staked[0].delegatee,
                    data.delegate_votes_changed[0].delegate
                )
                record = DelegationRecord(
                    delegator=data.staked[0].delegatee,
                    delegatee=data.delegate_votes_changed[0].delegate,
                    balance=latest_balance + data.staked[0].amount,
                    event_type=event_type,
                    blockNumber=block_number,
                    blockTimestamp=block_timestamp,
                    transactionHash=tx_hash
                )
                session.add(record)
            elif (
                    len(data.staked) == 1 and
                    len(data.delegate_votes_changed) == 2 and
                    (
                            data.delegate_votes_changed[0].previousBalance - data.delegate_votes_changed[0].newBalance
                    ) == (
                            data.delegate_votes_changed[1].newBalance - data.delegate_votes_changed[1].previousBalance
                    )
            ):
                # 0x0e12001d49195017c6090c5f3ea874e4dabfaa93f8f5081ebc1f5b2a69ff9f2f
                # need to update records of two keepers
                record1 = DelegationRecord(
                    delegator=data.staked[0].delegatee,
                    delegatee=data.delegate_votes_changed[0].delegate,
                    balance=data.delegate_votes_changed[0].newBalance,
                    event_type=event_type,
                    blockNumber=block_number,
                    blockTimestamp=block_timestamp,
                    transactionHash=tx_hash
                )
                # make sure its committed as this might affect the latest balance
                # when delegatee for both records is the same
                session.add(record1)
                session.commit()
                latest_balance = self.get_latest_balance(
                    session,
                    data.staked[0].delegatee,
                    data.delegate_votes_changed[1].delegate
                )
                record2 = DelegationRecord(
                    delegator=data.staked[0].delegatee,
                    delegatee=data.delegate_votes_changed[1].delegate,
                    balance=latest_balance + data.staked[0].amount,
                    event_type=event_type,
                    blockNumber=block_number,
                    blockTimestamp=block_timestamp,
                    transactionHash=tx_hash
                )
                session.add(record2)
            else:
                raise Exception('Unknown type')
        elif event_type == EventType.CTX_TRANSFER:
            if len(data.transfer) == 1 and len(data.delegate_votes_changed) == 1:
                # 0xeab6d157a81eaf7bab8682adf130a6136b566bc686f07fe7da213e54bab3a210
                # 0xfb6353f0be46485e28702ee903b59251f1d7fe81b0afdef707244f773fa54a02
                transfer_from = self.get_latest_balance(
                    session,
                    data.transfer[0].from_,
                    data.delegate_votes_changed[0].delegate
                )
                transfer_to = self.get_latest_balance(
                    session,
                    data.transfer[0].to,
                    data.delegate_votes_changed[0].delegate
                )
                if transfer_from:
                    # 0xeab6d157a81eaf7bab8682adf130a6136b566bc686f07fe7da213e54bab3a210
                    record = DelegationRecord(
                        delegator=data.transfer[0].from_,
                        delegatee=data.delegate_votes_changed[0].delegate,
                        balance=transfer_from - data.transfer[0].amount,
                        event_type=event_type,
                        blockNumber=block_number,
                        blockTimestamp=block_timestamp,
                        transactionHash=tx_hash
                    )
                else:
                    # 0xfb6353f0be46485e28702ee903b59251f1d7fe81b0afdef707244f773fa54a02
                    record = DelegationRecord(
                        delegator=data.transfer[0].to,
                        delegatee=data.delegate_votes_changed[0].delegate,
                        balance=transfer_to + data.transfer[0].amount,
                        event_type=event_type,
                        blockNumber=block_number,
                        blockTimestamp=block_timestamp,
                        transactionHash=tx_hash
                    )
                session.add(record)
            elif (
                    len(data.transfer) > 1 and
                    len(data.delegate_votes_changed) == 1 and
                    data.transfer[-2].to == data.transfer[-1].from_ and
                    data.transfer[-1].amount == (
                            data.delegate_votes_changed[0].newBalance - data.delegate_votes_changed[0].previousBalance)
            ):
                # exchange buy ctx
                # 0xd35185f3135f135390874086b095d137d3152f86fbff26b70f4754ff15abf289
                # delegatee = data.transfer[1].to
                # delegate = data.delegate_votes_changed[0].delegate

                # exchange buy ctx
                # 0x4e6960173537b3b8c4ecb1aeafd6680b2d0146e5169de70fc277cc24948644ad
                # delegatee = data.transfer[2].to
                # delegate = data.delegate_votes_changed[0].delegate
                latest_balance = self.get_latest_balance(
                    session,
                    data.transfer[-1].to,
                    data.delegate_votes_changed[0].delegate
                )
                record = DelegationRecord(
                    delegator=data.transfer[-1].to,
                    delegatee=data.delegate_votes_changed[0].delegate,
                    balance=latest_balance + data.transfer[-1].amount,
                    event_type=event_type,
                    blockNumber=block_number,
                    blockTimestamp=block_timestamp,
                    transactionHash=tx_hash
                )
                session.add(record)
            elif (
                    len(data.transfer) > 1 and
                    len(data.delegate_votes_changed) == 1 and
                    data.transfer[0].to == data.transfer[1].from_ and
                    data.transfer[0].amount == (
                            data.delegate_votes_changed[0].previousBalance - data.delegate_votes_changed[0].newBalance)
            ):
                # exchange sell
                # 0x300666908ec0581ef83e5f535734e6714aff5e46eb908511be773fd3466b310b
                # 0xadec3a0a4a5de690f90b9cd608948a748cafd6f8710d6e70a3601e22cd0f2c9e
                latest_balance = self.get_latest_balance(
                    session,
                    data.transfer[0].from_,
                    data.delegate_votes_changed[0].delegate
                )
                record = DelegationRecord(
                    delegator=data.transfer[0].from_,
                    delegatee=data.delegate_votes_changed[0].delegate,
                    balance=latest_balance - data.transfer[0].amount,
                    event_type=event_type,
                    blockNumber=block_number,
                    blockTimestamp=block_timestamp,
                    transactionHash=tx_hash
                )
                session.add(record)
            elif all([
                self.check_if_team_multisig(obj.delegate) for obj in data.delegate_votes_changed
            ]):
                # cryptex team multisig distribution
                # 0x32e6249c2425b3b9eee65f0a749708db6ae23f66e7b7cc036d4b25f1101f596e
                pass
            elif any([self.check_if_team_multisig(obj.delegate) for obj in data.delegate_votes_changed]):
                # cryptex team multisig distribution
                delegations = [obj for obj in data.delegate_votes_changed if
                               not self.check_if_team_multisig(obj.delegate)]
                amounts = [obj.amount for obj in data.transfer]
                for _delegate_votes_changed in delegations:
                    if self.check_if_team_multisig(_delegate_votes_changed.delegate):
                        continue
                    for _transfer in data.transfer:
                        # 0x67e594578941b0bc7e2d1e654d554ac672a307667adcacc11137c5a2067453ce
                        # 0x04cb7a6842b3398a0a964df8854f04a8de3309940a97735f1392dd3edd3a8e21
                        if (
                                _transfer.to == _delegate_votes_changed.delegate and
                                _delegate_votes_changed.delegate == '0xb8c30017b375bf675c2836c4c6b6ed5be214739d'
                        # ugly but only special case
                        ):
                            latest_balance = self.get_latest_balance(
                                session,
                                _transfer.to,
                                _delegate_votes_changed.delegate
                            )
                            record = DelegationRecord(
                                delegator=_transfer.to,
                                delegatee=_delegate_votes_changed.delegate,
                                balance=latest_balance + _transfer.amount,
                                event_type=event_type,
                                blockNumber=block_number,
                                blockTimestamp=block_timestamp,
                                transactionHash=tx_hash
                            )
                            session.add(record)
                            session.commit()
                            break
                    else:
                        for _transfer in data.transfer:
                            # 0x3c3d5c4250aea782d9666c5a99fcbaeb4889294bd26f5f90c7befc093ed96955
                            if ((
                                    _delegate_votes_changed.newBalance - _delegate_votes_changed.previousBalance
                            ) == _transfer.amount
                            ):
                                latest_balance = self.get_latest_balance(
                                    session,
                                    _transfer.to,
                                    _delegate_votes_changed.delegate
                                )
                                record = DelegationRecord(
                                    delegator=_transfer.to,
                                    delegatee=_delegate_votes_changed.delegate,
                                    balance=latest_balance + _transfer.amount,
                                    event_type=event_type,
                                    blockNumber=block_number,
                                    blockTimestamp=block_timestamp,
                                    transactionHash=tx_hash
                                )
                                session.add(record)
                                session.commit()
                                break
                        else:
                            raise Exception('Unknown type')
            else:
                raise Exception('Unknown type')
        elif event_type == EventType.WITHDRAWN:
            if len(data.withdrawn) == 1 and len(data.delegate_votes_changed) == 1:
                # 0x557200d874e5e6e5ce8b7a2aa23b4d72cf0d05b8ad2691d234480700da3d49a9
                latest_balance = self.get_latest_balance(
                    session,
                    data.transfer[0].to,
                    data.delegate_votes_changed[0].delegate
                )
                record = DelegationRecord(
                    delegator=data.withdrawn[0].delegatee,
                    delegatee=data.delegate_votes_changed[0].delegate,
                    balance=latest_balance + (data.delegate_votes_changed[0].newBalance - data.delegate_votes_changed[
                        0].previousBalance),
                    event_type=event_type,
                    blockNumber=block_number,
                    blockTimestamp=block_timestamp,
                    transactionHash=tx_hash
                )
                session.add(record)
            elif (
                    len(data.withdrawn) == 1 and
                    len(data.delegate_votes_changed) == 2 and
                    (
                            data.delegate_votes_changed[0].previousBalance - data.delegate_votes_changed[0].newBalance
                    ) == (
                            data.delegate_votes_changed[1].newBalance - data.delegate_votes_changed[1].previousBalance
                    )
            ):
                # 0xe95e3675994188e944ecda0ec3865bb4a9b8326f9ec2acfac19d6bdf87c6c4fd
                latest_balance1 = self.get_latest_balance(
                    session,
                    data.transfer[0].to,
                    data.delegate_votes_changed[0].delegate
                )
                record1 = DelegationRecord(
                    delegator=data.transfer[0].to,
                    delegatee=data.delegate_votes_changed[0].delegate,
                    balance=latest_balance1 + (data.delegate_votes_changed[0].newBalance - data.delegate_votes_changed[
                        0].previousBalance),
                    event_type=event_type,
                    blockNumber=block_number,
                    blockTimestamp=block_timestamp,
                    transactionHash=tx_hash
                )
                session.add(record1)
                session.commit()
                latest_balance2 = self.get_latest_balance(
                    session,
                    data.withdrawn[0].delegatee,
                    data.delegate_votes_changed[1].delegate
                )
                record2 = DelegationRecord(
                    delegator=data.withdrawn[0].delegatee,
                    delegatee=data.delegate_votes_changed[1].delegate,
                    balance=latest_balance2 + (data.delegate_votes_changed[1].newBalance - data.delegate_votes_changed[
                        1].previousBalance),
                    event_type=event_type,
                    blockNumber=block_number,
                    blockTimestamp=block_timestamp,
                    transactionHash=tx_hash
                )
                session.add(record2)
            else:
                raise Exception('Unknown type')
        else:
            raise Exception('Unknown type')
        session.commit()

    @staticmethod
    def check_if_team_multisig(address):
        return address == CRYPTEX_TEAM_MULTISIG_ADDRESS

    @staticmethod
    def get_latest_balance(session, delegator, delegatee) -> Decimal:
        old_record = session.query(DelegationRecord).filter(
            and_(
                DelegationRecord.delegator == delegator,
                DelegationRecord.delegatee == delegatee
            ),
        ).order_by(DelegationRecord.blockNumber.desc()).first()
        if old_record:
            return old_record.balance
        else:
            return Decimal("0")

    @staticmethod
    def classify_event_type(session, tx_hash):
        delegate_changed = session.query(DelegateChanged).filter(
            DelegateChanged.transactionHash == tx_hash
        ).all()
        delegate_votes_changed = session.query(DelegateVotesChanged).filter(
            DelegateVotesChanged.transactionHash == tx_hash
        ).all()
        staked = session.query(Staked).filter(
            Staked.transactionHash == tx_hash
        ).all()
        transfer = session.query(Transfer).filter(
            Transfer.transactionHash == tx_hash
        ).all()
        withdrawn = session.query(Withdrawn).filter(
            Withdrawn.transactionHash == tx_hash
        ).all()
        event_data = EventData(
            delegate_changed=delegate_changed,
            delegate_votes_changed=delegate_votes_changed,
            staked=staked,
            transfer=transfer,
            withdrawn=withdrawn
        )
        data = [delegate_changed, delegate_votes_changed, staked, transfer, withdrawn]
        data_exists_list = [bool(obj) for obj in data]
        # any([len(obj) > 1 for obj in [delegate_changed, staked, transfer, withdrawn]]) or
        if len(delegate_votes_changed) > 2 and not delegate_votes_changed[
                                                       0].delegate == '0xa70b638b70154edfcbb8dbbbd04900f328f32c35':
            raise Exception("length > 1 case. Please check the code")

        if data_exists_list == CTX_DELEGATION_CHECK:
            return EventType.DIRECT_DELEGATION, event_data
        elif data_exists_list == STAKED_CHECK:
            return EventType.STAKED, event_data
        elif data_exists_list == CTX_TRANSFER_CHECK:
            return EventType.CTX_TRANSFER, event_data
        elif data_exists_list == WITHDRAWN_CHECK:
            return EventType.WITHDRAWN, event_data
        else:
            raise Exception('Unknown type')


def get_keeper_votes_on_proposals():
    with Session() as session:
        return session.query(VoteCast.voter, func.count(VoteCast.voter)).group_by(VoteCast.voter).order_by(
            func.count(VoteCast.voter).desc()).all()


class VoteStatBuilder:

    def build(self):
        with Session() as session:
            for delegator, delegatee in self.fetch_delegator_delegatee_pair(session):
                for proposal_id, in self.fetch_all_proposals_id(session):
                    vote_cast = self.fetch_delegate_voted_on_proposal(session, proposal_id, delegatee)
                    if not vote_cast:
                        continue
                    else:
                        self.check_days_staked_and_create_record(session, proposal_id, delegator, delegatee, vote_cast)
            session.commit()

    def check_days_staked_and_create_record(self, session, proposal_id, delegator, delegatee, vote_cast):
        no_of_days_staked, balance = self.calculate_no_days_staked_before_vote(session, delegator, delegatee, vote_cast)
        if no_of_days_staked:
            vote_stat = VoteStat(
                delegator=delegator,
                delegatee=delegatee,
                proposalId=proposal_id,
                balance=balance,
                no_of_days=no_of_days_staked,
            )
            session.add(vote_stat)

    @staticmethod
    def fetch_delegate_voted_on_proposal(session, proposal_id, delegatee):
        return session.query(VoteCast).filter(
            and_(VoteCast.proposalId == proposal_id, VoteCast.voter == delegatee)
        ).first()

    @staticmethod
    def fetch_delegator_delegatee_pair(session):
        return session.query(
            DelegationRecord.delegator, DelegationRecord.delegatee).group_by(
            DelegationRecord.delegator, DelegationRecord.delegatee
        ).all()

    @staticmethod
    def fetch_all_proposals_id(session):
        return session.query(VoteCast.proposalId).filter(VoteCast.voter != CRYPTEX_TEAM_MULTISIG_ADDRESS).distinct().order_by(VoteCast.proposalId).all()

    @staticmethod
    def calculate_no_days_staked_before_vote(session, delegator, delegatee, vote_cast):
        latest_zero_balance = session.query(DelegationRecord).filter(
            and_(DelegationRecord.delegator == delegator,
                 DelegationRecord.delegatee == delegatee,
                 DelegationRecord.balance == 0,
                 DelegationRecord.blockNumber >= START_BLOCK,
                 DelegationRecord.blockNumber < vote_cast.blockNumber)
        ).order_by(DelegationRecord.blockNumber.desc()).first()
        if latest_zero_balance:
            nearest_non_zero_entry = session.query(DelegationRecord).filter(
                and_(DelegationRecord.delegator == delegator,
                     DelegationRecord.delegatee == delegatee,
                     DelegationRecord.blockNumber > latest_zero_balance.blockNumber,
                     DelegationRecord.blockNumber < vote_cast.blockNumber)
            ).order_by(DelegationRecord.blockNumber).first()
            if nearest_non_zero_entry:
                latest_non_zero_entry = session.query(DelegationRecord).filter(
                    and_(DelegationRecord.delegator == delegator,
                         DelegationRecord.delegatee == delegatee,
                         DelegationRecord.balance > 0,
                         DelegationRecord.blockNumber < vote_cast.blockNumber)
                ).order_by(DelegationRecord.blockNumber.desc()).first()
                start_date = max(START_DATETIME, convert_epoch_to_datetime(nearest_non_zero_entry.blockTimestamp))
                return no_of_days(start_date,
                                  convert_epoch_to_datetime(vote_cast.blockTimestamp)), latest_non_zero_entry.balance
            else:
                return 0, 0
        else:
            nearest_non_zero_entry = session.query(DelegationRecord).filter(
                and_(DelegationRecord.delegator == delegator,
                     DelegationRecord.delegatee == delegatee,
                     DelegationRecord.blockNumber > START_BLOCK,
                     DelegationRecord.blockNumber < vote_cast.blockNumber)
            ).order_by(DelegationRecord.blockNumber).first()
            if nearest_non_zero_entry:
                latest_non_zero_entry = session.query(DelegationRecord).filter(
                    and_(DelegationRecord.delegator == delegator,
                         DelegationRecord.delegatee == delegatee,
                         DelegationRecord.balance > 0,
                         DelegationRecord.blockNumber < vote_cast.blockNumber)
                ).order_by(DelegationRecord.blockNumber.desc()).first()
                start_date = max(START_DATETIME, convert_epoch_to_datetime(nearest_non_zero_entry.blockTimestamp))
                return no_of_days(start_date,
                                  convert_epoch_to_datetime(vote_cast.blockTimestamp)), latest_non_zero_entry.balance
            else:
                return 0, 0


TOTAL_REWARD = 50_000
KEEPER_SPLIT = 0.2
USER_SPLIT = 1 - KEEPER_SPLIT
excel_file_path = 'distribution_data.xlsx'


def convert_from_wei(amount):
    return from_wei(amount, 'ether')


class GenerateDistribution:
    def __init__(self):
        self.balances = defaultdict(int)

    def generate(self):
        with Session() as session:
            keeper_vote_cast_data = self.fetch_keeper_vote_cast_data(session)
            self.fill_keeper_balances(keeper_vote_cast_data)
            self.fill_user_balances(session, keeper_vote_cast_data)
            df1 = pd.DataFrame(list(sorted(self.balances.items(), key=lambda x: -x[1])), columns=['address', 'reward'])
            df2 = pd.read_sql_table(
                VoteStat.__tablename__, session.bind
            ).drop(columns=['id']
                   ).rename(columns={'no_of_days': 'number of days staked', 'balance': 'delegated_amount'})
            df3 = pd.read_sql_table(DelegationRecord.__tablename__, session.bind).drop(
                columns=['id', 'event_type']).rename(columns={'balance': 'delegated_amount'})
            df4 = pd.DataFrame(keeper_vote_cast_data, columns=['Keeper', 'No of Proposals voted on'])

        df1['address'] = df1['address'].apply(to_checksum_address)
        df2['delegator'] = df2['delegator'].apply(to_checksum_address)
        df2['delegatee'] = df2['delegatee'].apply(to_checksum_address)
        df2['delegated_amount'] = df2['delegated_amount'].apply(convert_from_wei)
        df3['delegator'] = df3['delegator'].apply(to_checksum_address)
        df3['delegatee'] = df3['delegatee'].apply(to_checksum_address)
        df3['delegated_amount'] = df3['delegated_amount'].apply(convert_from_wei)

        with pd.ExcelWriter(excel_file_path, engine='xlsxwriter') as writer:
            df1.to_excel(writer, sheet_name='Distribution', index=False)
            df2.to_excel(writer, sheet_name='Voting Stats', index=False)
            df3.to_excel(writer, sheet_name='Delegation Data', index=False)
            df4.to_excel(writer, sheet_name='Keeper Votes', index=False)

        df1['reward'] = df1['reward'].apply(int)
        df1.to_json('distribution.json', orient='records', lines=True)

    def fill_user_balances(self, session, keeper_vote_cast_data):
        total_weight_for_distribution = sum(obj[1] for obj in keeper_vote_cast_data)
        for keeper, no_proposals in keeper_vote_cast_data:
            # keeper_delgators_reward = (no_proposals * USER_SPLIT * TOTAL_REWARD) / total_weight_for_distribution
            # keeper_delegators_reward_per_proposal = keeper_delgators_reward / no_proposals
            for proposal_id, in session.query(VoteCast.proposalId).filter(VoteCast.voter == keeper):
                proposal_delegators = session.query(
                    VoteStat.delegator, VoteStat.balance, VoteStat.no_of_days
                ).filter(and_(VoteStat.delegatee == keeper, VoteStat.proposalId == proposal_id)).all()
                proposal_keeper_total_weight = sum(obj[1] * obj[2] for obj in proposal_delegators)
                for delegator, balance, no_of_days in proposal_delegators:
                    # self.balances[delegator] += (
                    #     int(balance) * no_of_days * keeper_delegators_reward_per_proposal
                    # ) / int(proposal_keeper_total_weight)
                    self.balances[delegator] += (
                        int(balance) * no_of_days * no_proposals * USER_SPLIT * TOTAL_REWARD
                    ) / (total_weight_for_distribution * no_proposals * int(proposal_keeper_total_weight))

    def fill_keeper_balances(self, keeper_vote_cast_data):
        total_keeper_reward = KEEPER_SPLIT * TOTAL_REWARD
        total_weight = sum(obj[1] for obj in keeper_vote_cast_data)
        for voter, no_of_proposals in keeper_vote_cast_data:
            self.balances[voter] += (no_of_proposals * total_keeper_reward) / total_weight

    @staticmethod
    def fetch_keeper_vote_cast_data(session):
        return session.query(
            VoteCast.voter, func.count(VoteCast.voter)
        ).filter(VoteCast.voter != CRYPTEX_TEAM_MULTISIG_ADDRESS, VoteCast.votes > 0).group_by(VoteCast.voter).order_by(func.count(VoteCast.voter).desc()).all()
