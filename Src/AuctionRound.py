class AuctionRound:
    def __init__(self):
        self.bids = []

    def place_bid(self, bid):
        self.bids.append(bid)

    def find_highest_bids(self):
        highest_bids = {}
        for bid in self.bids:
            if bid.block_id not in highest_bids or bid.amount > highest_bids[bid.block_id].amount:
                highest_bids[bid.block_id] = bid
        return highest_bids