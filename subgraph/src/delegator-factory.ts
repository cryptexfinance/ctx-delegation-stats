import {
  DelegatorCreated as DelegatorCreatedEvent,
  OwnershipTransferred as OwnershipTransferredEvent,
  RewardAdded as RewardAddedEvent,
  RewardPaid as RewardPaidEvent,
  RewardsDurationUpdated as RewardsDurationUpdatedEvent,
  Staked as StakedEvent,
  WaitTimeUpdated as WaitTimeUpdatedEvent,
  Withdrawn as WithdrawnEvent
} from "../generated/DelegatorFactory/DelegatorFactory"
import {
  DelegatorCreated,
  OwnershipTransferred,
  RewardAdded,
  RewardPaid,
  RewardsDurationUpdated,
  Staked,
  WaitTimeUpdated,
  Withdrawn
} from "../generated/schema"

export function handleDelegatorCreated(event: DelegatorCreatedEvent): void {
  let entity = new DelegatorCreated(
    event.transaction.hash.concatI32(event.logIndex.toI32())
  )
  entity.delegator = event.params.delegator
  entity.delegatee = event.params.delegatee

  entity.blockNumber = event.block.number
  entity.blockTimestamp = event.block.timestamp
  entity.transactionHash = event.transaction.hash

  entity.save()
}

export function handleOwnershipTransferred(
  event: OwnershipTransferredEvent
): void {
  let entity = new OwnershipTransferred(
    event.transaction.hash.concatI32(event.logIndex.toI32())
  )
  entity.previousOwner = event.params.previousOwner
  entity.newOwner = event.params.newOwner

  entity.blockNumber = event.block.number
  entity.blockTimestamp = event.block.timestamp
  entity.transactionHash = event.transaction.hash

  entity.save()
}

export function handleRewardAdded(event: RewardAddedEvent): void {
  let entity = new RewardAdded(
    event.transaction.hash.concatI32(event.logIndex.toI32())
  )
  entity.reward = event.params.reward

  entity.blockNumber = event.block.number
  entity.blockTimestamp = event.block.timestamp
  entity.transactionHash = event.transaction.hash

  entity.save()
}

export function handleRewardPaid(event: RewardPaidEvent): void {
  let entity = new RewardPaid(
    event.transaction.hash.concatI32(event.logIndex.toI32())
  )
  entity.user = event.params.user
  entity.reward = event.params.reward

  entity.blockNumber = event.block.number
  entity.blockTimestamp = event.block.timestamp
  entity.transactionHash = event.transaction.hash

  entity.save()
}

export function handleRewardsDurationUpdated(
  event: RewardsDurationUpdatedEvent
): void {
  let entity = new RewardsDurationUpdated(
    event.transaction.hash.concatI32(event.logIndex.toI32())
  )
  entity.newDuration = event.params.newDuration

  entity.blockNumber = event.block.number
  entity.blockTimestamp = event.block.timestamp
  entity.transactionHash = event.transaction.hash

  entity.save()
}

export function handleStaked(event: StakedEvent): void {
  let entity = new Staked(
    event.transaction.hash.concatI32(event.logIndex.toI32())
  )
  entity.delegator = event.params.delegator
  entity.delegatee = event.params.delegatee
  entity.amount = event.params.amount

  entity.blockNumber = event.block.number
  entity.blockTimestamp = event.block.timestamp
  entity.transactionHash = event.transaction.hash

  entity.save()
}

export function handleWaitTimeUpdated(event: WaitTimeUpdatedEvent): void {
  let entity = new WaitTimeUpdated(
    event.transaction.hash.concatI32(event.logIndex.toI32())
  )
  entity.waitTime = event.params.waitTime

  entity.blockNumber = event.block.number
  entity.blockTimestamp = event.block.timestamp
  entity.transactionHash = event.transaction.hash

  entity.save()
}

export function handleWithdrawn(event: WithdrawnEvent): void {
  let entity = new Withdrawn(
    event.transaction.hash.concatI32(event.logIndex.toI32())
  )
  entity.delegator = event.params.delegator
  entity.delegatee = event.params.delegatee
  entity.amount = event.params.amount

  entity.blockNumber = event.block.number
  entity.blockTimestamp = event.block.timestamp
  entity.transactionHash = event.transaction.hash

  entity.save()
}
