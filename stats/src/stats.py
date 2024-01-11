from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import and_

from .database import Session
from .models import (
    DelegateChanged,
    DelegateVotesChanged,
    Staked,
    Transfer,
    Withdrawn,
    DelegationRecord,
    EventType
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


class BuildAccountDelegation:

    def generate_stats(self):
        with Session() as session:
            subquery = session.query(
                DelegateVotesChanged.blockNumber, DelegateVotesChanged.transactionHash
            ).distinct(DelegateVotesChanged.transactionHash).subquery()
            for delegate_vote_changed in session.query(
                    subquery.c.transactionHash, subquery.c.blockNumber
            ).order_by(subquery.c.blockNumber).all():
                event_type, data = self.classify_event_type(
                    session,
                    delegate_vote_changed.transactionHash
                )
                self.write_record(
                    session,
                    delegate_vote_changed.transactionHash,
                    delegate_vote_changed.blockNumber,
                    event_type,
                    data
                )

    def write_record(self, session, tx_hash, block_number, event_type, data):
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
                    balance=latest_balance + data.delegate_votes_changed[0].newBalance - data.delegate_votes_changed[0].previousBalance,
                    event_type=event_type,
                    blockNumber=block_number,
                    transactionHash=tx_hash
                )
                session.add(record)
            elif len(data.delegate_changed) == 1 and len(data.delegate_votes_changed) == 2 and data.delegate_votes_changed[0].newBalance == 0:
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
                    balance=latest_balance2 + (data.delegate_votes_changed[0].newBalance - data.delegate_votes_changed[0].previousBalance),
                    event_type=event_type,
                    blockNumber=block_number,
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
                    balance=latest_balance2 + (data.delegate_votes_changed[1].newBalance - data.delegate_votes_changed[1].previousBalance),
                    event_type=event_type,
                    blockNumber=block_number,
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
                        transactionHash=tx_hash
                    )
                session.add(record)
            elif (
                    len(data.transfer) > 1 and
                    len(data.delegate_votes_changed) == 1 and
                    data.transfer[-2].to == data.transfer[-1].from_ and
                    data.transfer[-1].amount == (data.delegate_votes_changed[0].newBalance - data.delegate_votes_changed[0].previousBalance)
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
                    transactionHash=tx_hash
                )
                session.add(record)
            elif (
                    len(data.transfer) > 1 and
                    len(data.delegate_votes_changed) == 1 and
                    data.transfer[0].to == data.transfer[1].from_ and
                    data.transfer[0].amount == (data.delegate_votes_changed[0].previousBalance - data.delegate_votes_changed[0].newBalance)
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
                delegations = [obj for obj in data.delegate_votes_changed if not self.check_if_team_multisig(obj.delegate)]
                amounts = [obj.amount for obj in data.transfer]
                for _delegate_votes_changed in delegations:
                    if self.check_if_team_multisig(_delegate_votes_changed.delegate):
                        continue
                    # if amounts.count(_delegate_votes_changed.newBalance - _delegate_votes_changed.previousBalance) > 1:
                    #     import pdb; pdb.set_trace()
                    #     """"""
                    for _transfer in data.transfer:
                        # 0x67e594578941b0bc7e2d1e654d554ac672a307667adcacc11137c5a2067453ce
                        # 0x04cb7a6842b3398a0a964df8854f04a8de3309940a97735f1392dd3edd3a8e21
                        if (
                                _transfer.to == _delegate_votes_changed.delegate and
                                _delegate_votes_changed.delegate == '0xb8c30017b375bf675c2836c4c6b6ed5be214739d'  # ugly but only special case
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
                    balance=latest_balance + (data.delegate_votes_changed[0].newBalance - data.delegate_votes_changed[0].previousBalance),
                    event_type=event_type,
                    blockNumber=block_number,
                    transactionHash=tx_hash
                )
                session.add(record)
            elif (
                    len(data.withdrawn) == 1 and
                    len(data.delegate_votes_changed) == 2 and
                    (
                        data.delegate_votes_changed[0].previousBalance -  data.delegate_votes_changed[0].newBalance
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
                    balance=latest_balance1 + (data.delegate_votes_changed[0].newBalance - data.delegate_votes_changed[0].previousBalance),
                    event_type=event_type,
                    blockNumber=block_number,
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
                    balance=latest_balance2 + (data.delegate_votes_changed[1].newBalance - data.delegate_votes_changed[1].previousBalance),
                    event_type=event_type,
                    blockNumber=block_number,
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
        if len(delegate_votes_changed) > 2 and not delegate_votes_changed[0].delegate == '0xa70b638b70154edfcbb8dbbbd04900f328f32c35':
            raise Exception("length > 1 case. Please check the code")

        if data_exists_list == CTX_DELEGATION_CHECK :
            return EventType.DIRECT_DELEGATION, event_data
        elif data_exists_list == STAKED_CHECK:
            return EventType.STAKED, event_data
        elif data_exists_list == CTX_TRANSFER_CHECK:
            return EventType.CTX_TRANSFER, event_data
        elif data_exists_list == WITHDRAWN_CHECK:
            return EventType.WITHDRAWN, event_data
        else:
            raise Exception('Unknown type')
