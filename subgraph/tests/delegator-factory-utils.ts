import { newMockEvent } from "matchstick-as"
import { ethereum, Address, BigInt } from "@graphprotocol/graph-ts"
import {
  DelegatorCreated,
  OwnershipTransferred,
  RewardAdded,
  RewardPaid,
  RewardsDurationUpdated,
  Staked,
  WaitTimeUpdated,
  Withdrawn
} from "../generated/DelegatorFactory/DelegatorFactory"

export function createDelegatorCreatedEvent(
  delegator: Address,
  delegatee: Address
): DelegatorCreated {
  let delegatorCreatedEvent = changetype<DelegatorCreated>(newMockEvent())

  delegatorCreatedEvent.parameters = new Array()

  delegatorCreatedEvent.parameters.push(
    new ethereum.EventParam("delegator", ethereum.Value.fromAddress(delegator))
  )
  delegatorCreatedEvent.parameters.push(
    new ethereum.EventParam("delegatee", ethereum.Value.fromAddress(delegatee))
  )

  return delegatorCreatedEvent
}

export function createOwnershipTransferredEvent(
  previousOwner: Address,
  newOwner: Address
): OwnershipTransferred {
  let ownershipTransferredEvent = changetype<OwnershipTransferred>(
    newMockEvent()
  )

  ownershipTransferredEvent.parameters = new Array()

  ownershipTransferredEvent.parameters.push(
    new ethereum.EventParam(
      "previousOwner",
      ethereum.Value.fromAddress(previousOwner)
    )
  )
  ownershipTransferredEvent.parameters.push(
    new ethereum.EventParam("newOwner", ethereum.Value.fromAddress(newOwner))
  )

  return ownershipTransferredEvent
}

export function createRewardAddedEvent(reward: BigInt): RewardAdded {
  let rewardAddedEvent = changetype<RewardAdded>(newMockEvent())

  rewardAddedEvent.parameters = new Array()

  rewardAddedEvent.parameters.push(
    new ethereum.EventParam("reward", ethereum.Value.fromUnsignedBigInt(reward))
  )

  return rewardAddedEvent
}

export function createRewardPaidEvent(
  user: Address,
  reward: BigInt
): RewardPaid {
  let rewardPaidEvent = changetype<RewardPaid>(newMockEvent())

  rewardPaidEvent.parameters = new Array()

  rewardPaidEvent.parameters.push(
    new ethereum.EventParam("user", ethereum.Value.fromAddress(user))
  )
  rewardPaidEvent.parameters.push(
    new ethereum.EventParam("reward", ethereum.Value.fromUnsignedBigInt(reward))
  )

  return rewardPaidEvent
}

export function createRewardsDurationUpdatedEvent(
  newDuration: BigInt
): RewardsDurationUpdated {
  let rewardsDurationUpdatedEvent = changetype<RewardsDurationUpdated>(
    newMockEvent()
  )

  rewardsDurationUpdatedEvent.parameters = new Array()

  rewardsDurationUpdatedEvent.parameters.push(
    new ethereum.EventParam(
      "newDuration",
      ethereum.Value.fromUnsignedBigInt(newDuration)
    )
  )

  return rewardsDurationUpdatedEvent
}

export function createStakedEvent(
  delegator: Address,
  delegatee: Address,
  amount: BigInt
): Staked {
  let stakedEvent = changetype<Staked>(newMockEvent())

  stakedEvent.parameters = new Array()

  stakedEvent.parameters.push(
    new ethereum.EventParam("delegator", ethereum.Value.fromAddress(delegator))
  )
  stakedEvent.parameters.push(
    new ethereum.EventParam("delegatee", ethereum.Value.fromAddress(delegatee))
  )
  stakedEvent.parameters.push(
    new ethereum.EventParam("amount", ethereum.Value.fromUnsignedBigInt(amount))
  )

  return stakedEvent
}

export function createWaitTimeUpdatedEvent(waitTime: BigInt): WaitTimeUpdated {
  let waitTimeUpdatedEvent = changetype<WaitTimeUpdated>(newMockEvent())

  waitTimeUpdatedEvent.parameters = new Array()

  waitTimeUpdatedEvent.parameters.push(
    new ethereum.EventParam(
      "waitTime",
      ethereum.Value.fromUnsignedBigInt(waitTime)
    )
  )

  return waitTimeUpdatedEvent
}

export function createWithdrawnEvent(
  delegator: Address,
  delegatee: Address,
  amount: BigInt
): Withdrawn {
  let withdrawnEvent = changetype<Withdrawn>(newMockEvent())

  withdrawnEvent.parameters = new Array()

  withdrawnEvent.parameters.push(
    new ethereum.EventParam("delegator", ethereum.Value.fromAddress(delegator))
  )
  withdrawnEvent.parameters.push(
    new ethereum.EventParam("delegatee", ethereum.Value.fromAddress(delegatee))
  )
  withdrawnEvent.parameters.push(
    new ethereum.EventParam("amount", ethereum.Value.fromUnsignedBigInt(amount))
  )

  return withdrawnEvent
}
