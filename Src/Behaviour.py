import math
import random

def randomBehaviour():
    behaviourList = ["B"]
    return random.choice(behaviourList)

def genBehaviour(input):
    match input:
        case "A":
            return typeA()
        case "B":
            return typeB()
        case _:
            print("Invalid behaviour type")
            return None

# Example behaviour class, any new types should follow the same variable-names and functions
class typeA:
    def __init__(self):
        self.aggressiveness = random.uniform(0.8, 0.9)  # How "aggressive" bids are, effectively scales the bid size
        self.marketPriceFactor = random.uniform(0.8, 1)  # How many % of marketprice (price per unit) to bid with
        self.stopBid = random.uniform(1, 1.1)  # In which range of the expected price to stop bidding at
        self.bidLikelyhood = random.uniform(0.8, 1)

    # Higher level function to run the adaptive updates
    def updateVariables(self, currentRound, maxRound):
        self.adaptiveAggressiveness(currentRound, maxRound)
        self.adaptiveMPFactor(currentRound, maxRound)
        self.adaptiveStopBid(currentRound, maxRound)

    # Can create functions in order to scale the aggressivity depending on how many rounds of auctions are left
    def adaptiveAggressiveness(self, currentRound, maxRound):
        self.aggressiveness = self.aggressiveness * 1

    # Can create functions to scale bid size depending on how many rounds of auctions are left
    def adaptiveMPFactor(self, currentRound, maxRound):
        self.marketPriceFactor = self.marketPriceFactor * 1

    # Insert functions to scale bid stop depending on how many rounds of auctions are left
    def adaptiveStopBid(self, currentRound, maxRound):
        self.stopBid = self.stopBid * 1

    # Return the likelyhood of bidding depending on various factors available
    # Will be compared to a random value in range [0,1], returning 0.8 will be 80% likelyhood to bid etc
    # bidIndex: number of bidding opportunities in the current set of auctions
    # unfulfilledNeed: % of need which is unfulfilled
    # distance: % of distance limit (to be able to favor auctions in close proximity etc)
    def adaptiveBidLikelyhoood(self, currentRound, maxRound, bidIndex, unfulfilledNeed, distance):
        return self.bidLikelyhood * 1


class typeB:
    def __init__(self):
        self.aggressiveness = random.uniform(0.4, 0.6)      # How "aggressive" bids are, effectively scales the bid size
        self.marketPriceFactor = random.uniform(0.8, 1)     # How many % of marketprice (price per unit) to bid with
        self.stopBid = random.uniform(1, 1.1)               # In which range of the expected price to stop bidding at
        self.bidLikelyhood = random.uniform(0.8, 1)

    # Higher level function to run the adaptive updates
    def updateVariables(self, currentRound, maxRound):
        self.adaptiveAggressiveness(currentRound, maxRound)
        self.adaptiveMPFactor(currentRound, maxRound)
        self.adaptiveStopBid(currentRound, maxRound)

    # Can create functions in order to scale the aggressivity depending on how many rounds of auctions are left
    def adaptiveAggressiveness(self, currentRound, maxRound):
        self.aggressiveness = self.aggressiveness * 1

    # Can create functions to scale bid size depending on how many rounds of auctions are left
    def adaptiveMPFactor(self, currentRound, maxRound):
        self.marketPriceFactor = self.marketPriceFactor * 1
    
    # Insert functions to scale bid stop depending on how many rounds of auctions are left
    def adaptiveStopBid(self, currentRound, maxRound):
        self.stopBid = self.stopBid * 1

    # Return the likelyhood of bidding depending on various factors available
    # Will be compared to a random value in range [0,1], returning 0.8 will be 80% likelyhood to bid etc
    # bidIndex: number of bidding opportunities in the current set of auctions
    # unfulfilledNeed: % of need which is unfulfilled
    # distance: % of distance limit (to be able to favor auctions in close proximity etc)
    def adaptiveBidLikelyhoood(self, currentRound, maxRound, bidIndex, unfulfilledNeed, distance):
        return self.bidLikelyhood * 1
