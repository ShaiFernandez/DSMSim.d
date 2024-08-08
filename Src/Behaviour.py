import math
import random

def randomBehaviour():
    behaviourList = ["D", "E", "F"]
    return random.choice(behaviourList)

def genBehaviour(input, aggressiveness, marketPriceFactor, stopBid, bidLikelihood):
    match input:
        case "A":
            return typeA(aggressiveness, marketPriceFactor, stopBid, bidLikelihood)
        case "B":
            return typeB(aggressiveness, marketPriceFactor, stopBid, bidLikelihood)
        case "C":
            return typeC(aggressiveness, marketPriceFactor, stopBid, bidLikelihood)
        case "D":
            return typeD(aggressiveness, marketPriceFactor, stopBid, bidLikelihood)
        case "E":
            return typeE(aggressiveness, marketPriceFactor, stopBid, bidLikelihood)
        case "F":
            return typeF(aggressiveness, marketPriceFactor, stopBid, bidLikelihood)
        case _:
            print("Invalid behaviour type")
            return None

# Example behaviour class, any new types should follow the same variable-names and functions
class typeA:
    def __init__(self, aggressiveness, marketPriceFactor, stopBid, bidLikelihood):
        #self.aggressiveness = random.uniform(0.8, 0.9)  # How "aggressive" bids are, effectively scales the bid size
        #self.marketPriceFactor = random.uniform(0.9, 1.5)  # How many % of marketprice (price per unit) to bid with
        #self.stopBid = random.uniform(1, 2)  # In which range of the expected price to stop bidding at
        #self.bidLikelihood = random.uniform(0.8, 1)
        self.aggressiveness = 0.8
        self.marketPriceFactor = 1.5  # How many % of marketprice (price per unit) to bid with
        self.stopBid = 2  # In which range of the expected price to stop bidding at
        self.bidLikelihood = 1.1 #0.9


    # Higher level function to run the adaptive updates
    def updateVariables(self, currentRound, maxRound, unfulfilledNeed):
        if unfulfilledNeed > 0.5:
            self.aggressiveness *= 1.1  # Increase aggressiveness if unfulfilled need is high
        else:
            self.aggressiveness *= 0.9  # Decrease aggressiveness if unfulfilled need is low

        progress_ratio = currentRound / maxRound
        if progress_ratio > 0.75:
            self.bidLikelihood += 0.2  # Increase bid likelihood in the final quarters
            self.aggressiveness *= 1.2  # Increase aggressiveness in the late stages

    def updateVariablesRound(self, currentRound, maxRound, difference):
        if difference > 0:
            self.aggressiveness *= 1.1  # Increase aggressiveness if unfulfilled need is high
        else:
            self.aggressiveness *= 0.9  # Decrease aggressiveness if unfulfilled need is low

        progress_ratio = currentRound / maxRound
        if progress_ratio > 0.75:
            self.bidLikelihood += 0.2  # Increase bid likelihood in the final quarters
            self.aggressiveness *= 1.2  # Increase aggressiveness in the late stages

    def asdict(self):
        return {'behavior_type': "A", 'aggressiveness': self.aggressiveness, 'marketPriceFactor': self.marketPriceFactor, 'stopBid': self.stopBid, 'bidLikelihood': self.bidLikelihood}


class typeB:
    def __init__(self, aggressiveness, marketPriceFactor, stopBid, bidLikelihood):
        #self.aggressiveness = random.uniform(0.5, 0.8)      # How "aggressive" bids are, effectively scales the bid size
        #self.marketPriceFactor = random.uniform(0.8, 1.3)  # How many % of marketprice (price per unit) to bid with
        #self.stopBid = random.uniform(1, 1.5)  # In which range of the expected price to stop bidding at
        #self.bidLikelihood = random.uniform(0.6, 0.9)
        self.aggressiveness = 0.6
        self.marketPriceFactor = 1.3     # How many % of marketprice (price per unit) to bid with
        self.stopBid = 1.5             # In which range of the expected price to stop bidding at
        self.bidLikelihood = 1.1 #0.7

    # Higher level function to run the adaptive updates
    def updateVariables(self, currentRound, maxRound, unfulfilledNeed):
        if unfulfilledNeed > 0.5:
            self.aggressiveness *= 1.1  # Increase aggressiveness if unfulfilled need is high
        else:
            self.aggressiveness *= 0.9  # Decrease aggressiveness if unfulfilled need is low

        progress_ratio = currentRound / maxRound
        if progress_ratio > 0.75:
            self.bidLikelihood += 0.1  # Increase bid likelihood in the final quarters
            self.aggressiveness *= 1.15  # Increase aggressiveness in the late stages

    def updateVariablesRound(self, currentRound, maxRound, difference):
        if difference > 0:
            self.aggressiveness *= 1.1  # Increase aggressiveness if unfulfilled need is high
        else:
            self.aggressiveness *= 0.9  # Decrease aggressiveness if unfulfilled need is low

        progress_ratio = currentRound / maxRound
        if progress_ratio > 0.75:
            self.bidLikelihood += 0.1  # Increase bid likelihood in the final quarters
            self.aggressiveness *= 1.15  # Increase aggressiveness in the late stages

    def asdict(self):
        return {'behavior_type': "B", 'aggressiveness': self.aggressiveness, 'marketPriceFactor': self.marketPriceFactor, 'stopBid': self.stopBid, 'bidLikelihood': self.bidLikelihood}


class typeC:
    def __init__(self, aggressiveness, marketPriceFactor, stopBid, bidLikelihood):
        #self.aggressiveness = random.uniform(0.3, 0.5)      # How "aggressive" bids are, effectively scales the bid size
        #self.marketPriceFactor = random.uniform(0.7, 1.1)  # How many % of marketprice (price per unit) to bid with
        #self.stopBid = random.uniform(1, 1.25)  # In which range of the expected price to stop bidding at
        #self.bidLikelihood = random.uniform(0.4, 0.7)
        self.aggressiveness = 0.4
        self.marketPriceFactor = 1.1     # How many % of marketprice (price per unit) to bid with
        self.stopBid = 1.25              # In which range of the expected price to stop bidding at
        self.bidLikelihood = 1.1 #0.5

    # Higher level function to run the adaptive updates
    def updateVariables(self, currentRound, maxRound, unfulfilledNeed):
        if unfulfilledNeed > 0.5:
            self.aggressiveness *= 1.1  # Increase aggressiveness if unfulfilled need is high
        else:
            self.aggressiveness *= 0.9  # Decrease aggressiveness if unfulfilled need is low

        progress_ratio = currentRound / maxRound
        if progress_ratio > 0.75:
            self.bidLikelihood += 0.05  # Increase bid likelihood in the final quarters
            self.aggressiveness *= 1.1  # Increase aggressiveness in the late stages

    def updateVariablesRound(self, currentRound, maxRound, difference):
        if difference > 0:
            self.aggressiveness *= 1.1  # Increase aggressiveness if unfulfilled need is high
        else:
            self.aggressiveness *= 0.9  # Decrease aggressiveness if unfulfilled need is low

        progress_ratio = currentRound / maxRound
        if progress_ratio > 0.75:
            self.bidLikelihood += 0.05  # Increase bid likelihood in the final quarters
            self.aggressiveness *= 1.1  # Increase aggressiveness in the late stages

    def asdict(self):
        return {'behavior_type': "C", 'aggressiveness': self.aggressiveness, 'marketPriceFactor': self.marketPriceFactor, 'stopBid': self.stopBid, 'bidLikelihood': self.bidLikelihood}


class typeD:
    def __init__(self, aggressiveness, marketPriceFactor, stopBid, bidLikelihood):
        self.aggressiveness = 0.5  # How "aggressive" bids are, effectively scales the bid size
        #self.marketPriceFactor = random.uniform(0.9, 1.5)  # How many % of marketprice (price per unit) to bid with
        #self.stopBid = random.uniform(1, 2)  # In which range of the expected price to stop bidding at
        #self.bidLikelihood = random.uniform(0.8, 1)
        self.marketPriceFactor = 1.5  # How many % of marketprice (price per unit) to bid with
        self.stopBid = 2  # In which range of the expected price to stop bidding at
        self.bidLikelihood = 1.1#0.9

    # Higher level function to run the adaptive updates
    def updateVariables(self, currentRound, maxRound, unfulfilledNeed):
        if unfulfilledNeed > 0.5:
            self.aggressiveness *= 1.1  # Increase aggressiveness if unfulfilled need is high
        else:
            self.aggressiveness *= 0.9  # Decrease aggressiveness if unfulfilled need is low

        progress_ratio = currentRound / maxRound
        if progress_ratio > 0.75:
            self.bidLikelihood += 0.2  # Increase bid likelihood in the final quarters
            self.aggressiveness *= 1.2  # Increase aggressiveness in the late stages


    def updateVariablesRound(self, currentRound, maxRound, difference):
        if difference > 0:
            self.aggressiveness *= 1.1  # Increase aggressiveness if unfulfilled need is high
        else:
            self.aggressiveness *= 0.9  # Decrease aggressiveness if unfulfilled need is low

        progress_ratio = currentRound / maxRound
        if progress_ratio > 0.75:
            self.bidLikelihood += 0.2  # Increase bid likelihood in the final quarters
            self.aggressiveness *= 1.2  # Increase aggressiveness in the late stages

    def asdict(self):
        return {'behavior_type': "D", 'aggressiveness': self.aggressiveness, 'marketPriceFactor': self.marketPriceFactor, 'stopBid': self.stopBid, 'bidLikelihood': self.bidLikelihood}


class typeE:
    def __init__(self, aggressiveness, marketPriceFactor, stopBid, bidLikelihood):
        self.aggressiveness = 0.5      # How "aggressive" bids are, effectively scales the bid size
        #self.marketPriceFactor = random.uniform(0.8, 1.3)     # How many % of marketprice (price per unit) to bid with
        #self.stopBid = random.uniform(1, 1.5)               # In which range of the expected price to stop bidding at
        #self.bidLikelihood = random.uniform(0.6, 0.9)
        self.marketPriceFactor = 1.3  # How many % of marketprice (price per unit) to bid with
        self.stopBid = 1.5  # In which range of the expected price to stop bidding at
        self.bidLikelihood = 1.1#0.7

    # Higher level function to run the adaptive updates
    def updateVariables(self, currentRound, maxRound, unfulfilledNeed):
        if unfulfilledNeed > 0.5:
            self.aggressiveness *= 1.1  # Increase aggressiveness if unfulfilled need is high
        else:
            self.aggressiveness *= 0.9  # Decrease aggressiveness if unfulfilled need is low

        progress_ratio = currentRound / maxRound
        if progress_ratio > 0.75:
            self.bidLikelihood += 0.1  # Increase bid likelihood in the final quarters
            self.aggressiveness *= 1.15  # Increase aggressiveness in the late stages


    def updateVariablesRound(self, currentRound, maxRound, difference):
        if difference > 0:
            self.aggressiveness *= 1.1  # Increase aggressiveness if unfulfilled need is high
        else:
            self.aggressiveness *= 0.9  # Decrease aggressiveness if unfulfilled need is low

        progress_ratio = currentRound / maxRound
        if progress_ratio > 0.75:
            self.bidLikelihood += 0.1  # Increase bid likelihood in the final quarters
            self.aggressiveness *= 1.15  # Increase aggressiveness in the late stages

    def asdict(self):
        return {'behavior_type': "E", 'aggressiveness': self.aggressiveness, 'marketPriceFactor': self.marketPriceFactor, 'stopBid': self.stopBid, 'bidLikelihood': self.bidLikelihood}


class typeF:
    def __init__(self, aggressiveness, marketPriceFactor, stopBid, bidLikelihood):
        self.aggressiveness = 0.5      # How "aggressive" bids are, effectively scales the bid size
        #self.marketPriceFactor = random.uniform(0.7, 1.1)     # How many % of marketprice (price per unit) to bid with
        #self.stopBid = random.uniform(1, 1.25)               # In which range of the expected price to stop bidding at
        #self.bidLikelihood = random.uniform(0.4, 0.7)
        self.marketPriceFactor = 1.1  # How many % of marketprice (price per unit) to bid with
        self.stopBid = 1.25  # In which range of the expected price to stop bidding at
        self.bidLikelihood = 1.1#0.5

    # Higher level function to run the adaptive updates
    def updateVariables(self, currentRound, maxRound, unfulfilledNeed):
        if unfulfilledNeed > 0.5:
            self.aggressiveness *= 1.1  # Increase aggressiveness if unfulfilled need is high
        else:
            self.aggressiveness *= 0.9  # Decrease aggressiveness if unfulfilled need is low

        progress_ratio = currentRound / maxRound
        if progress_ratio > 0.75:
            self.bidLikelihood += 0.05  # Increase bid likelihood in the final quarters
            self.aggressiveness *= 1.1  # Increase aggressiveness in the late stages

    def updateVariablesRound(self, currentRound, maxRound, difference):
        if difference > 0:
            self.aggressiveness *= 1.1  # Increase aggressiveness if unfulfilled need is high
        else:
            self.aggressiveness *= 0.9  # Decrease aggressiveness if unfulfilled need is low

        progress_ratio = currentRound / maxRound
        if progress_ratio > 0.75:
            self.bidLikelihood += 0.05  # Increase bid likelihood in the final quarters
            self.aggressiveness *= 1.1  # Increase aggressiveness in the late stages

    def asdict(self):
        return {'behavior_type': "F", 'aggressiveness': self.aggressiveness, 'marketPriceFactor': self.marketPriceFactor, 'stopBid': self.stopBid, 'bidLikelihood': self.bidLikelihood}