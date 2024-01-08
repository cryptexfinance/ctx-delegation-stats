from enum import Enum
from dataclasses import dataclass
from .database import Session
from .models import (
    DelegateChanged,
    DelegateVotesChanged,
    Staked,
    Transfer,
    Withdrawn,
    DelegationRecord
)


class EventType(Enum):
    DIRECT_DELEGATION = 1
    STAKED = 2
    CTX_TRANSFER = 3
    WITHDRAWN = 4


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

    @staticmethod
    def write_record(session, tx_hash, block_number, event_type, data):
        record = DelegationRecord(blockNumber=block_number, transactionHash=tx_hash)
        if event_type == EventType.DIRECT_DELEGATION:
            if len(data.delegate_changed) == 1 and len(data.delegate_votes_changed) == 1:
                ...
            elif len(data.delegate_changed) == 1 and len(data.delegate_votes_changed) == 2 and data.delegate_votes_changed[0].newBalance == 0:
                # delegator changed; old delegator balance becomes 0, new one gets 1st event previousBalance.
                # Also for the 2nd event newBalance - oldBalance = previousBalance of 1st event
                # 0x0dc8bca57fbf2d4c283a1130e29d51c927a7cb93c0dcc297b157ea4936fe0fd3
                ...
            else:
                raise Exception('Unknown type')
        elif event_type == EventType.STAKED:
            if len(data.staked) == 1 and len(data.delegate_votes_changed) == 1:
                ...
            elif (
                    len(data.staked) == 1 and
                    len(data.delegate_votes_changed) == 2 and
                    (
                        data.delegate_votes_changed[0].previousBalance -  data.delegate_votes_changed[0].newBalance
                    ) == (
                        data.delegate_votes_changed[1].newBalance - data.delegate_votes_changed[1].previousBalance
                    )
            ):
                # 0x0e12001d49195017c6090c5f3ea874e4dabfaa93f8f5081ebc1f5b2a69ff9f2f
                # need to update records of two keepers
                ...
            else:
                raise Exception('Unknown type')
        elif event_type == EventType.CTX_TRANSFER:
            if len(data.transfer) == 1 and len(data.delegate_votes_changed) == 1:
                ...
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
                ...
            elif (
                    len(data.transfer) > 1 and
                    len(data.delegate_votes_changed) == 1 and
                    data.transfer[0].to == data.transfer[1].from_ and
                    data.transfer[0].amount == (data.delegate_votes_changed[0].previousBalance - data.delegate_votes_changed[0].newBalance)
            ):
                # exchange sell
                # 0x300666908ec0581ef83e5f535734e6714aff5e46eb908511be773fd3466b310b
                # 0xadec3a0a4a5de690f90b9cd608948a748cafd6f8710d6e70a3601e22cd0f2c9e
                ...
            elif all([
                obj.delegate == '0xa70b638b70154edfcbb8dbbbd04900f328f32c35' for obj in data.delegate_votes_changed
            ]):
                # cryptex team multisig distribution
                # 0x32e6249c2425b3b9eee65f0a749708db6ae23f66e7b7cc036d4b25f1101f596e
                pass
            elif any([obj.delegate == '0xa70b638b70154edfcbb8dbbbd04900f328f32c35' for obj in data.delegate_votes_changed]):
                # cryptex team multisig distribution
                delegations = [obj for obj in data.delegate_votes_changed if obj.delegate != '0xa70b638b70154edfcbb8dbbbd04900f328f32c35']
                for _delegate_votes_changed in delegations:
                    for _transfer in data.transfer:
                        # 0x67e594578941b0bc7e2d1e654d554ac672a307667adcacc11137c5a2067453ce
                        if _transfer.to == _delegate_votes_changed.delegate:
                            # save record
                            break
                    else:
                        for _transfer in data.transfer:
                            # 0x3c3d5c4250aea782d9666c5a99fcbaeb4889294bd26f5f90c7befc093ed96955
                            if (_delegate_votes_changed.newBalance - _delegate_votes_changed.previousBalance) == _transfer.amount:
                                # save record
                                break
                        else:
                            raise Exception('Unknown type')
            else:
                raise Exception('Unknown type')
        elif event_type == EventType.WITHDRAWN:
            if len(data.withdrawn) == 1 and len(data.delegate_votes_changed) == 1:
                ...
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
                ...
            else:
                raise Exception('Unknown type')
        else:
            raise Exception('Unknown type')
        # session.add(record)
        # session.commit()

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
