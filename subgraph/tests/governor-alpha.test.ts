import {
  assert,
  describe,
  test,
  clearStore,
  beforeAll,
  afterAll
} from "matchstick-as/assembly/index"
import { BigInt, Address, Bytes } from "@graphprotocol/graph-ts"
import { ProposalCanceled } from "../generated/schema"
import { ProposalCanceled as ProposalCanceledEvent } from "../generated/GovernorAlpha/GovernorAlpha"
import { handleProposalCanceled } from "../src/governor-alpha"
import { createProposalCanceledEvent } from "./governor-alpha-utils"

// Tests structure (matchstick-as >=0.5.0)
// https://thegraph.com/docs/en/developer/matchstick/#tests-structure-0-5-0

describe("Describe entity assertions", () => {
  beforeAll(() => {
    let id = BigInt.fromI32(234)
    let newProposalCanceledEvent = createProposalCanceledEvent(id)
    handleProposalCanceled(newProposalCanceledEvent)
  })

  afterAll(() => {
    clearStore()
  })

  // For more test scenarios, see:
  // https://thegraph.com/docs/en/developer/matchstick/#write-a-unit-test

  test("ProposalCanceled created and stored", () => {
    assert.entityCount("ProposalCanceled", 1)

    // 0xa16081f360e3847006db660bae1c6d1b2e17ec2a is the default address used in newMockEvent() function

    // More assert options:
    // https://thegraph.com/docs/en/developer/matchstick/#asserts
  })
})
