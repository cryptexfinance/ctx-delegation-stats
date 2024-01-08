import {
  ProposalCanceled as ProposalCanceledEvent,
  ProposalCreated as ProposalCreatedEvent,
  ProposalExecuted as ProposalExecutedEvent,
  ProposalQueued as ProposalQueuedEvent,
  VoteCast as VoteCastEvent
} from "../generated/GovernorAlpha/GovernorAlpha"
import {
  GovernorAlphaProposalCanceled,
  GovernorAlphaProposalCreated,
  GovernorAlphaProposalExecuted,
  GovernorAlphaProposalQueued,
  GovernorAlphaVoteCast
} from "../generated/schema"

export function handleProposalCanceled(event: ProposalCanceledEvent): void {
  let entity = new GovernorAlphaProposalCanceled(
    event.transaction.hash.concatI32(event.logIndex.toI32())
  )
  entity.GovernorAlpha_id = event.params.id

  entity.blockNumber = event.block.number
  entity.blockTimestamp = event.block.timestamp
  entity.transactionHash = event.transaction.hash

  entity.save()
}

export function handleProposalCreated(event: ProposalCreatedEvent): void {
  let entity = new GovernorAlphaProposalCreated(
    event.transaction.hash.concatI32(event.logIndex.toI32())
  )
  entity.GovernorAlpha_id = event.params.id
  entity.proposer = event.params.proposer
  entity.startBlock = event.params.startBlock
  entity.endBlock = event.params.endBlock
  entity.description = event.params.description

  entity.blockNumber = event.block.number
  entity.blockTimestamp = event.block.timestamp
  entity.transactionHash = event.transaction.hash

  entity.save()
}

export function handleProposalExecuted(event: ProposalExecutedEvent): void {
  let entity = new GovernorAlphaProposalExecuted(
    event.transaction.hash.concatI32(event.logIndex.toI32())
  )
  entity.GovernorAlpha_id = event.params.id

  entity.blockNumber = event.block.number
  entity.blockTimestamp = event.block.timestamp
  entity.transactionHash = event.transaction.hash

  entity.save()
}

export function handleProposalQueued(event: ProposalQueuedEvent): void {
  let entity = new GovernorAlphaProposalQueued(
    event.transaction.hash.concatI32(event.logIndex.toI32())
  )
  entity.GovernorAlpha_id = event.params.id
  entity.eta = event.params.eta

  entity.blockNumber = event.block.number
  entity.blockTimestamp = event.block.timestamp
  entity.transactionHash = event.transaction.hash

  entity.save()
}

export function handleVoteCast(event: VoteCastEvent): void {
  let entity = new GovernorAlphaVoteCast(
    event.transaction.hash.concatI32(event.logIndex.toI32())
  )
  entity.voter = event.params.voter
  entity.proposalId = event.params.proposalId
  entity.support = event.params.support
  entity.votes = event.params.votes

  entity.blockNumber = event.block.number
  entity.blockTimestamp = event.block.timestamp
  entity.transactionHash = event.transaction.hash

  entity.save()
}
