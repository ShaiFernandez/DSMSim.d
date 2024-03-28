import math
import random

def randomBehaviour():
    behaviourList = ["A", "B"]
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
        self.bidLikelihood = random.uniform(0.8, 1)

    # Higher level function to run the adaptive updates
    def updateVariables(self, currentRound, maxRound, unfulfilledNeed):
        if unfulfilledNeed > 0.5:
            self.aggressiveness *= 1.1  # Increase aggressiveness if unfulfilled need is high
        else:
            self.aggressiveness *= 0.9  # Decrease aggressiveness if unfulfilled need is low

        progress_ratio = currentRound / maxRound
        if progress_ratio > 0.75:
            self.bidLikelihood += 0.1  # Increase bid likelihood in the final quarters
            self.aggressiveness *= 1.2  # Increase aggressiveness in the late stages


class typeB:
    def __init__(self):
        self.aggressiveness = random.uniform(0.4, 0.6)      # How "aggressive" bids are, effectively scales the bid size
        self.marketPriceFactor = random.uniform(0.8, 1)     # How many % of marketprice (price per unit) to bid with
        self.stopBid = random.uniform(1, 1.1)               # In which range of the expected price to stop bidding at
        self.bidLikelihood = random.uniform(0.8, 1)

    # Higher level function to run the adaptive updates
    def updateVariables(self, currentRound, maxRound, unfulfilledNeed):
        if unfulfilledNeed > 0.5:
            self.aggressiveness *= 1.1  # Increase aggressiveness if unfulfilled need is high
        else:
            self.aggressiveness *= 0.9  # Decrease aggressiveness if unfulfilled need is low

        progress_ratio = currentRound / maxRound
        if progress_ratio > 0.75:
            self.bidLikelihood += 0.1  # Increase bid likelihood in the final quarters
            self.aggressiveness *= 1.2  # Increase aggressiveness in the late stages