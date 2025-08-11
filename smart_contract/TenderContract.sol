// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Tender {
    address public owner;
    address public winner;
    uint public lowestBid = type(uint).max;
    address[] public bidders;
    mapping(address => uint) public bids;

    constructor(string memory _title) {
        owner = msg.sender;
    }

    function placeBid() public payable {
        require(msg.value < lowestBid, "Bid too high");
        bids[msg.sender] = msg.value;
        lowestBid = msg.value;
        bidders.push(msg.sender);
    }

    function declareWinner() public {
        require(msg.sender == owner, "Only owner can declare winner");
        winner = address(0);
        uint lowest = type(uint).max;
        for (uint i = 0; i < bidders.length; i++) {
            if (bids[bidders[i]] < lowest) {
                lowest = bids[bidders[i]];
                winner = bidders[i];
            }
        }
    }
}
