// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TenderContract {
    address public tenderOwner;
    string public title;
    string public description;

    struct Bid {
        address bidder;
        uint256 amount;
    }

    Bid[] public bids;

    constructor(string memory _title, string memory _description) {
        tenderOwner = msg.sender;
        title = _title;
        description = _description;
    }

    function placeBid() public payable {
        require(msg.value > 0, "Bid amount must be greater than zero");

        bids.push(Bid({
            bidder: msg.sender,
            amount: msg.value
        }));
    }

    function getTotalBids() public view returns (uint) {
        return bids.length;
    }

    function getBid(uint index) public view returns (address, uint256) {
        require(index < bids.length, "Invalid index");
        Bid memory bid = bids[index];
        return (bid.bidder, bid.amount);
    }

    function getAllBids() public view returns (address[] memory, uint256[] memory) {
        address[] memory bidders = new address[](bids.length);
        uint256[] memory amounts = new uint256[](bids.length);

        for (uint i = 0; i < bids.length; i++) {
            bidders[i] = bids[i].bidder;
            amounts[i] = bids[i].amount;
        }

        return (bidders, amounts);
    }
}
