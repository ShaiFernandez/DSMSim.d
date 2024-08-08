import math
from itertools import combinations, permutations
from collections import deque

import json

def evaluateCombinations(combinations):
    "Function to compute data to sort by such as fairness and avg distance"
    output = []
    for combo in combinations:  # For each valid set of buyer-block combinations
        # Compute Raj Jain's Fairness index and average distance between sellers and buyers
        nom = 0
        denom = 0
        avgDistance = 0
        avgPrice = 0
        for buyerSet in combo:  # For each buyer-blocks match
            avgDistance += buyerSet['distanceSum']
            nom += buyerSet['pricePerUnit']
            denom += buyerSet['pricePerUnit']**2
        avgPrice = nom / len(combo)
        nom = nom**2
        denom = denom * len(combo)
        avgDistance /= len(combo)
        output.append({'combo':combo, 'fairness':nom/denom, 'avgDistance':avgDistance, 'avgPrice':avgPrice})
    #Sort by fairness
    sortedOutput = sorted(output, key=lambda i:i['fairness'], reverse=True)
    #Sort by avgDistance
    #sortedOutput = sorted(output, key=lambda i:i['avgDistance'], reverse=True)
