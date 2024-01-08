import {
  assert,
  describe,
  test,
  clearStore,
  beforeAll,
  afterAll
} from "matchstick-as/assembly/index"
import { Address, BigInt } from "@graphprotocol/graph-ts"
import { DelegatorCreated } from "../generated/schema"
import { DelegatorCreated as DelegatorCreatedEvent } from "../generated/DelegatorFactory/DelegatorFactory"
import { handleDelegatorCreated } from "../src/delegator-factory"
import { createDelegatorCreatedEvent } from "./delegator-factory-utils"

// Tests structure (matchstick-as >=0.5.0)
// https://thegraph.com/docs/en/developer/matchstick/#tests-structure-0-5-0

describe("Describe entity assertions", () => {
  beforeAll(() => {
    let delegator = Address.fromString(
      "0x0000000000000000000000000000000000000001"
    )
    let delegatee = Address.fromString(
      "0x0000000000000000000000000000000000000001"
    )
    let newDelegatorCreatedEvent = createDelegatorCreatedEvent(
      delegator,
      delegatee
    )
    handleDelegatorCreated(newDelegatorCreatedEvent)
  })

  afterAll(() => {
    clearStore()
  })

  // For more test scenarios, see:
  // https://thegraph.com/docs/en/developer/matchstick/#write-a-unit-test

  test("DelegatorCreated created and stored", () => {
    assert.entityCount("DelegatorCreated", 1)

    // 0xa16081f360e3847006db660bae1c6d1b2e17ec2a is the default address used in newMockEvent() function
    assert.fieldEquals(
      "DelegatorCreated",
      "0xa16081f360e3847006db660bae1c6d1b2e17ec2a-1",
      "delegator",
      "0x0000000000000000000000000000000000000001"
    )
    assert.fieldEquals(
      "DelegatorCreated",
      "0xa16081f360e3847006db660bae1c6d1b2e17ec2a-1",
      "delegatee",
      "0x0000000000000000000000000000000000000001"
    )

    // More assert options:
    // https://thegraph.com/docs/en/developer/matchstick/#asserts
  })
})
