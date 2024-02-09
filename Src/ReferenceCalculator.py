import math
from itertools import combinations, permutations
from collections import deque

import json

def matchMakingCalculation(sellerList, bidderList):
    blocks = getBlocks(sellerList)
    permNum = 0
    permComb = 0
    validCombinations = []
    print(f"Beginning matchmaking calculation\n {int((len(blocks) / 2) + 1) * math.comb(len(blocks), len(bidderList))* len(blocks)} combinations to test")

    for perm in permutations(blocks):
        print(f"perm: {perm}")
        for rot in listRotator(perm):
            print(f"rot: {rot}")
            for combination in splitfinder(rot, len(bidderList)):
                print(f"combination: {combination}")
                if(validateCombination(combination, bidderList)):
                    validCombinations.append(formatCombination(combination, bidderList))
                permComb +=1
        permNum += 1

        print(f"Permutation number {permNum} / {int((len(blocks) / 2) + 1)}\nCombinations tested: {permComb}")
        
        if(permNum > len(blocks)/2): break
        # Due to the way permutations are listed in the permutation-function this will have tested all relevant possibilities given that the lists have also been rotated.
    if(len(validCombinations) == 0):
        return None
    validCombinations = evaluateCombinations(validCombinations)

    #Returns the results
    return validCombinations

def getBlocks(sellerList):
    "Extract the blocks and sellers and format in handleable manner"
    blocks = []
    for seller in sellerList:
        sellerBlockList = seller.LinkOfBlocks.display()
        for block in sellerBlockList:
            blocks.append((block, seller))
    return blocks

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
    return sortedOutput
    
        

# Combination format is a list with (number of buyers)+1 lists within, each containing (block,seller) tuples, combination[-1] containing "unbought" blocks
def validateCombination(combination, buyers):
    "Function to determine if a combination of blocks is valid"
    # Validate if the order of buying blocks is broken
    for block in combination[-1]:
        if(not checkIfPreviousBlockUnbought(block[0], combination[:len(combination)-2])):
            return False

    # Validate if every buyer has a fulfilled need
    for i in range(len(buyers)):
        need = buyers[i].needs
        for block in combination[i]:
            need -= block[0].Amount
        if(need > 0): return False
    return True

def formatCombination(combination, buyers):
    "Process and format combination data to be saved, compute fairness, distance data etc"
    combinationData = []
    for i in range(len(buyers)):
        temp = {'buyer':buyers[i],'blocks':combination[i]}
        quantity = 0
        price = 0
        distanceSum = 0                 # Sum up the distance of sales, sqrt((x2-x1)^2 + (y2-y1)^2)
        for block in combination[i]:
            distanceSum += math.sqrt((buyers[i].location[0]-block[1].location[0])**2 + (buyers[i].location[1]-block[1].location[1])**2)
            quantity += block[0].Amount
            price += block[0].Price

        temp['pricePerUnit'] = round(price/quantity, 2)
        temp['distanceSum'] = round(distanceSum, 2)
        combinationData.append(temp)

    return combinationData
    

def listRotator(inputList):
    rotations = len(inputList)
    outputList = []
    inputList = deque(inputList)
    while rotations > 0:
        outputList.append(tuple(inputList))
        inputList.rotate(1)
        rotations -= 1
    
    return outputList

# Find all possible ways to split the blocks between the buyers (including one "buyer" for unbought blocks)
# Assumes that only the "unbought" blocks can be empty since every buyer should have a demand
# blocklist = All the blocks from the sellers arranged in a specific permutation
def splitfinder(blocklist, numBuyers):
    possibleSplits = []
    for breakpoints in combinations(range(1, len(blocklist) + 1), numBuyers):  # Combinatorics: find all places to place splitpoints between groups
        possibilityN = []

        possibilityN.append(list(blocklist[0: breakpoints[0]]))
        for i in range(0, numBuyers - 1):
            possibilityN.append(list(blocklist[breakpoints[i] : breakpoints[i + 1]]))
        possibilityN.append(list(blocklist[breakpoints[(len(breakpoints) - 1)]: (len(blocklist))]))

        possibleSplits.append(list(possibilityN))
    return possibleSplits

# Recursively check if a block that has to be bought after another block has been bought without this being the case
def checkIfPreviousBlockUnbought(unboughtBlock, boughtBlocks):
    if unboughtBlock.next() != None:
        for blockset in boughtBlocks:
            for block in blockset:
                if unboughtBlock.next() == block[0]:
                    return False
        return checkIfPreviousBlockUnbought(unboughtBlock.next(), boughtBlocks)
    else:
        return True