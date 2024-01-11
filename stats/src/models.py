import enum

from sqlalchemy import Column, Integer, BigInteger, String, Numeric, Enum

from .database import Base, engine


class DelegatorCreated(Base):
    __tablename__ = 'delegator_created'
    id = Column(String(100), unique=True, primary_key=True)
    delegator = Column(String(66))
    delegatee = Column(String(66))
    blockNumber = Column(BigInteger)
    blockTimestamp = Column(Integer)
    transactionHash = Column(String(66))


class Staked(Base):
    __tablename__ = 'staked'
    id = Column(String(100), unique=True, primary_key=True)
    delegator = Column(String(66))
    delegatee = Column(String(66))
    amount = Column(Numeric(precision=60, scale=0))
    blockNumber = Column(BigInteger)
    blockTimestamp = Column(Integer)
    transactionHash = Column(String(66))


class Withdrawn(Base):
    __tablename__ = 'withdrawn'
    id = Column(String(100), unique=True, primary_key=True)
    delegator = Column(String(66))
    delegatee = Column(String(66))
    amount = Column(Numeric(precision=60, scale=0))
    blockNumber = Column(BigInteger)
    blockTimestamp = Column(Integer)
    transactionHash = Column(String(66))


class DelegateChanged(Base):
    __tablename__ = 'delegate_changed'
    id = Column(String(100), unique=True, primary_key=True)
    delegator = Column(String(66))
    fromDelegate = Column(String(66))
    toDelegate = Column(String(66))
    blockNumber = Column(BigInteger)
    blockTimestamp = Column(Integer)
    transactionHash = Column(String(66))


class DelegateVotesChanged(Base):
    __tablename__ = 'delegate_votes_changed'
    id = Column(String(100), unique=True, primary_key=True)
    delegate = Column(String(66))
    previousBalance = Column(Numeric(precision=60, scale=0))
    newBalance = Column(Numeric(precision=60, scale=0))
    blockNumber = Column(BigInteger)
    blockTimestamp = Column(Integer)
    transactionHash = Column(String(66))


class Transfer(Base):
    __tablename__ = 'transfer'
    id = Column(String(100), unique=True, primary_key=True)
    from_ = Column(String(66))
    to = Column(String(66))
    amount = Column(Numeric(precision=60, scale=0))
    blockNumber = Column(BigInteger)
    blockTimestamp = Column(Integer)
    transactionHash = Column(String(66))


class EventType(enum.Enum):
    DIRECT_DELEGATION = 'DD'
    STAKED = 'ST'
    CTX_TRANSFER = 'CT'
    WITHDRAWN = 'WD'


class DelegationRecord(Base):
    __tablename__ = 'delegation_record'
    id = Column(Integer, primary_key=True, autoincrement=True)
    # user
    delegator = Column(String(66))
    # keeper
    delegatee = Column(String(66))
    event_type = Column(Enum(EventType))
    balance = Column(Numeric(precision=60, scale=0))
    blockNumber = Column(BigInteger)
    transactionHash = Column(String(66))


def create_db_models():
    Base.metadata.create_all(engine)
