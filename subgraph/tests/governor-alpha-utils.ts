import { newMockEvent } from "matchstick-as"
import { ethereum, BigInt, Address, Bytes } from "@graphprotocol/graph-ts"
import {
  ProposalCanceled,
  ProposalCreated,
  ProposalExecuted,
  ProposalQueued,
  VoteCast
} from "../generated/GovernorAlpha/GovernorAlpha"

export function createProposalCanceledEvent(id: BigInt): ProposalCanceled {
  let proposalCanceledEvent = changetype<ProposalCanceled>(newMockEvent())

  proposalCanceledEvent.parameters = new Array()

  proposalCanceledEvent.parameters.push(
    new ethereum.EventParam("id", ethereum.Value.fromUnsignedBigInt(id))
  )

  return proposalCanceledEvent
}

export function createProposalCreatedEvent(
  id: BigInt,
  proposer: Address,
  targets: Array<Address>,
  values: Array<BigInt>,
  signatures: Array<string>,
  calldatas: Array<Bytes>,
  startBlock: BigInt,
  endBlock: BigInt,
  description: string
): ProposalCreated {
  let proposalCreatedEvent = changetype<ProposalCreated>(newMockEvent())

  proposalCreatedEvent.parameters = new Array()

  proposalCreatedEvent.parameters.push(
    new ethereum.EventParam("id", ethereum.Value.fromUnsignedBigInt(id))
  )
  proposalCreatedEvent.parameters.push(
    new ethereum.EventParam("proposer", ethereum.Value.fromAddress(proposer))
  )
  proposalCreatedEvent.parameters.push(
    new ethereum.EventParam("targets", ethereum.Value.fromAddressArray(targets))
  )
  proposalCreatedEvent.parameters.push(
    new ethereum.EventParam(
      "values",
      ethereum.Value.fromUnsignedBigIntArray(values)
    )
  )
  proposalCreatedEvent.parameters.push(
    new ethereum.EventParam(
      "signatures",
      ethereum.Value.fromStringArray(signatures)
    )
  )
  proposalCreatedEvent.parameters.push(
    new ethereum.EventParam(
      "calldatas",
      ethereum.Value.fromBytesArray(calldatas)
    )
  )
  proposalCreatedEvent.parameters.push(
    new ethereum.EventParam(
      "startBlock",
      ethereum.Value.fromUnsignedBigInt(startBlock)
    )
  )
  proposalCreatedEvent.parameters.push(
    new ethereum.EventParam(
      "endBlock",
      ethereum.Value.fromUnsignedBigInt(endBlock)
    )
  )
  proposalCreatedEvent.parameters.push(
    new ethereum.EventParam(
      "description",
      ethereum.Value.fromString(description)
    )
  )

  return proposalCreatedEvent
}

export function createProposalExecutedEvent(id: BigInt): ProposalExecuted {
  let proposalExecutedEvent = changetype<ProposalExecuted>(newMockEvent())

  proposalExecutedEvent.parameters = new Array()

  proposalExecutedEvent.parameters.push(
    new ethereum.EventParam("id", ethereum.Value.fromUnsignedBigInt(id))
  )

  return proposalExecutedEvent
}

export function createProposalQueuedEvent(
  id: BigInt,
  eta: BigInt
): ProposalQueued {
  let proposalQueuedEvent = changetype<ProposalQueued>(newMockEvent())

  proposalQueuedEvent.parameters = new Array()

  proposalQueuedEvent.parameters.push(
    new ethereum.EventParam("id", ethereum.Value.fromUnsignedBigInt(id))
  )
  proposalQueuedEvent.parameters.push(
    new ethereum.EventParam("eta", ethereum.Value.fromUnsignedBigInt(eta))
  )

  return proposalQueuedEvent
}

export function createVoteCastEvent(
  voter: Address,
  proposalId: BigInt,
  support: boolean,
  votes: BigInt
): VoteCast {
  let voteCastEvent = changetype<VoteCast>(newMockEvent())

  voteCastEvent.parameters = new Array()

  voteCastEvent.parameters.push(
    new ethereum.EventParam("voter", ethereum.Value.fromAddress(voter))
  )
  voteCastEvent.parameters.push(
    new ethereum.EventParam(
      "proposalId",
      ethereum.Value.fromUnsignedBigInt(proposalId)
    )
  )
  voteCastEvent.parameters.push(
    new ethereum.EventParam("support", ethereum.Value.fromBoolean(support))
  )
  voteCastEvent.parameters.push(
    new ethereum.EventParam("votes", ethereum.Value.fromUnsignedBigInt(votes))
  )

  return voteCastEvent
}
