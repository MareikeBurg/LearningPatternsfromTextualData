import sys, os
sys.path.append(os.getcwd())

from src.knuth_morris_pratt import naive, knuthMorrisPratt
import string
from patternUtil import *


def preProcess(pattern, word, repeatingVar):
    # algo 2 in one rep pattern

    n = len(word)

    maxTermFactors = findMaximalTerminalFactors(pattern)
    print("\nmaxTermfactors", maxTermFactors)
    # each maxmial terminal factor is only needed once
    # line from https://stackoverflow.com/questions/3724551/python-uniqueness-for-list-of-lists
    uniqueMaxTermFactors = [list(x) for x in set(tuple(x) for x in maxTermFactors)] 
    print("uniqueMaxTermFactors", uniqueMaxTermFactors)

    d = {}
    for u in uniqueMaxTermFactors:

        posiblePositons = knuthMorrisPratt(word, u)

        di = []
        for i in range(0, n):

            x = list(filter(lambda x: x >= i, posiblePositons))
            
            if x:
                di.append(min(x))
            else:
                di.append(-1)

        d[tuple(u)] = di

    print("d: ", d)


    #factorise alpha: m is defined by the  number of betas
    w0, betaList, wiList, gammaList, wiDashList = factorisePattern(pattern, repeatingVar)
    m = len(betaList)
    M = [[-1 for _ in range(m)] for _ in range(n)]


    print("\nm:", m)
    print("betaList: ", betaList)

    for i in range(0,n):
        for j in range(0,m):
            maxTermFactorsBeta = findMaximalTerminalFactors(betaList[j])
            s = len(maxTermFactorsBeta)
            g = d[tuple(maxTermFactorsBeta[0])][i]


            #print(f"s: {s} g: {g} factors: {maxTermFactorsBeta}")
            for h in range(1,s):
                #print(f"h: {h}")
                g = d[tuple(maxTermFactorsBeta[h])][g + len(maxTermFactorsBeta[h-1])+1]
            
            #print(f"g: {g} len(maxTermFactorsBeta[s-1]: {len(maxTermFactorsBeta[s-1])}")
            M[i][j] = g + len(maxTermFactorsBeta[s-1]) + 1

    return M


# algo 3 with a fixed v
def matchingOneRep(pattern, word, repeatingVar):

    n = len(word)
    position0 = 0
    while not isVariable(pattern[position0]):
        if pattern[position0] != word[position0]:
            return False
        position0 += 1

    # todo not factorize in both functions, 46 is the nubmer for X, the repeating var
    w0, betaList, wiList, gammaList, wiDashList = factorisePattern(pattern, repeatingVar)
    m = len(betaList)
    M = preProcess(pattern, word, repeatingVar)
    factors = findAllFactors(word)

    # remeber to use w0 
    print("heere",m)
    for v in factors:
        pos = position0
        for i in range(0, m):
            pos += M[pos+1][i]
            alphaj = wiList[i] + fillVarWithWord(gammaList[i], v, repeatingVar) + wiDashList[i]
            find = knuthMorrisPratt(word[pos + 1:], alphaj )
            if find:
                piDash = find[0]
            else:
                piDash = n + 1
            
            if piDash <= n:
                pos = piDash + len(alphaj) - 1
            else:
                return False
        pos += M[pos + 1][m]
    
        # suffix check is not needed currently
        # since its done in the loop
    
    # if this works for all factors v it matches 
    return True



#pattern = convertToIntarray("aAbbbbBaaCbbaXaaXbbbXaaaaDaaaaEaa")
#word = convertToIntarray("aaaabbbbccaabbabfaabfbbbbfaaaacaaaaaaaa")
#word = convertToIntarray("aaaabbbbccaabbabfaabfbbbbfaaaacaaaaaaaa")
pattern = convertToIntarray("XbbXc")
word = convertToIntarray("abbac")

print("Pattern is: ", pattern)
print("word is: ", word)

# 46 is the number for X, the repeating var
print(preProcess(pattern, word, 46))
#print(matchingOneRep(pattern,word,46))

def matchingRegular(pattern, word):
    # matching problem for regular pattern

    w_i, prefix, suffix = findAllNonVariables(pattern)

    # check prefix
    j = len(prefix)
    if prefix != word[:j]:
        return False

    # main check
    for s in w_i:

        find = knuthMorrisPratt(word[j:], s)
        if find == []:
            return False
        else:
            j += find[0] + len(s)

    # check suffix
    # check if the suffix is not empty and only then whether it matches
    if suffix and suffix != word[-len(suffix) :]:
        return False

    return True


def descPat(sample):
    # creates a descriptive pattern from a sample of words, also automatically finds a shortest word

    word = sorted(sample, key=len)[0]

    m = len(word)
    alpha = []
    for i in range(m):
        alpha.append(i*2)
    #print(alpha)

    for i in range(m):
        #print("Current Alpha: ", alpha)

        q, j = True, 0

        # try replacing one variable with one terminal symbol
        newAlpha = alpha.copy()
        newAlpha[i] = word[i]

        # first test is whether the new pattern is still in its pattern class, actually not needed for regualar pattern
        if isRegularPatternClass(canonicalForm(newAlpha)):

            # next test if all words from the sample are still in the pattern language
            inSample = True
            for w in sample:
                # print(w, matchingRegular(newAlpha, w))
                if not matchingRegular(newAlpha, w):
                    inSample = False
                    break

            if inSample:
                alpha = newAlpha
                q = False

        # next try to replace variables with each other
        while q and j < i:
            if isVariable(alpha[j]):

                newAlpha = alpha.copy()
                newAlpha[i] = alpha[j]

                if isRegularPatternClass(canonicalForm(newAlpha)):

                    # next test if all words from the sample are still in the pattern language
                    inSample = True
                    for w in sample:
                        # print(w, matchingRegular(newAlpha, w))
                        if not matchingRegular(newAlpha, w):
                            inSample = False
                            break

                    if inSample:
                        alpha = newAlpha
                        q = False
                    else:
                        j += 1
            if q:
                j += 1

    return canonicalForm(removeVariablesInRow(alpha))


if __name__ == "__main__":

    """
    # test membership
    alpha = convertToIntarray("aAbaBc")
    word1 = convertToIntarray("abcbcbcbac")
    word2 = convertToIntarray("aaa")
    print(alpha,word1,word2)
    print(matchingRegular(alpha, word1))
    print(matchingRegular(alpha, word2))
    """
    
    #sample = [[1,3,5], [1,3,3,5],[1,3,3,3,5]]
    #print(descPat(sample))
    