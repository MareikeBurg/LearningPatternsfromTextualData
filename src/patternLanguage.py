
from knuth_morris_pratt import naive, knuthMorrisPratt
import string
from patternUtil import *


def preProcess(pattern, word,allBetaJs):
    # algo 2 in one rep pattern

    n = len(word)
    
    # each maxmial terminal factor is only needed once
    # line from https://stackoverflow.com/questions/3724551/python-uniqueness-for-list-of-lists
    maxTermFactors = findMaximalTerminalFactors(pattern)
    uniqueMaxTermFactors = [list(x) for x in set(tuple(x) for x in maxTermFactors)] 
    print(f"{maxTermFactors = }")
    print(f"{uniqueMaxTermFactors = }")

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

    print(f"{d = }\n")


    # -1 to make it continues with the rest, where there are m+1 betaJ that exits
    m = len(allBetaJs) - 1
    M = [[-1 for _ in range(m+1)] for _ in range(n)]


    print(f"{m = }")
    print(f"{allBetaJs = }")

    for i in range(0,n):
        for j in range(0,m+1):
            maxTermFactorsBeta = findMaximalTerminalFactors(allBetaJs[j])
            s = len(maxTermFactorsBeta)

            if s == 0:
                # then the bj is a single variable since there are no 2 var direclty after each other
                M[i][j] = i - 1

            elif s == 1:
                # then there is only a single maximal terminal factor in bj
                if d[tuple(maxTermFactorsBeta[0])][i] != - 1:
                    M[i][j] = d[tuple(maxTermFactorsBeta[0])][i] + len(maxTermFactorsBeta[0])
                else:
                    M[i][j] = None

            else:
                # there are s many maximal terminal factors
                print("does not happen")
            """
            g = d[tuple(maxTermFactorsBeta[0])][i]
            print(f"{s = } {maxTermFactorsBeta[0] = } {i = } {g = }")


            #print(f"s: {s} g: {g} factors: {maxTermFactorsBeta}")
            for h in range(1,s):
                #print(f"h: {h}")
                g = d[tuple(maxTermFactorsBeta[h])][g + len(maxTermFactorsBeta[h-1])+1]
            
            #print(f"g: {g} len(maxTermFactorsBeta[s-1]: {len(maxTermFactorsBeta[s-1])}")
            M[i][j] = g + len(maxTermFactorsBeta[s-1])+1
            """

    return M


# algo 3 with a fixed v
def matchingOneRep(pattern, word):

    # find the repeatingVar
    repeatingVar = isOneRepPatternClass(pattern)[1]
    #print(f"\n\n\n{pattern = } {word = } {repeatingVar = }")

    n = len(word)
    factorization = factorisePattern(pattern, repeatingVar)
    m = len(factorization["betaList"])

    M = preProcess(pattern, word, factorization["betaList"] + [factorization["betam+1"]])
    print(f"{factorization= } {M = }")

    posZero = len(factorization["w0"])

    if pattern[:posZero] != word[:posZero]:
        print(f"wrong prefix")
        return False

    factors = findAllFactors(word)


    for v in factors:

        pos = posZero
        matched = True

        for i in range(0, m):

            if M[pos][i] is None:
                matched = False
                break
            else:
                pos = M[pos][i] + 1
            
            alphaj = factorization["wiList"][i] + fillVarWithWord(factorization["gammaList"][i], v, repeatingVar) + factorization["wiDashList"][i]

            if factorization["betaList"][i] != []:
                find = knuthMorrisPratt(word[pos:], alphaj)
                if not find:
                    matched = False
                    break
                else:
                    print(f"{alphaj = } {pos = } {len(alphaj) = } {find[0] = } {i = }")
                    pos = len(alphaj) + find[0]
            else:
                if word[pos:len(alphaj)] != alphaj:
                    matched = False
                    break

        if matched:
            if factorization["betam+1"] != []:
                print(f"{pos = } {m = }")
                if M[pos][m] is not None:
                    pos = M[pos][m]

            if pattern[pos:] == factorization["wim+1"]:
                print(f"{v = }")
                return True
    
    return False


# 46 is the number for X, the repeating var

#pattern = convertToIntarray("aAbbaCbaXaXbXaaDccEb")
#word = convertToIntarray("aabbacbaxaxbxaadcceb")
#pattern = convertToIntarray("XbbXc")
#word = convertToIntarray("aabbac")
pattern = [0, 2, 0, 4, 6, 8]
word = [1, 3, 3, 5, 3, 3]

print(f"{pattern = }")
print(f"{word    = }")

#allBetaJs = factorization["betaList"] + [factorization["betam+1"]]
#print(preProcess(pattern, word, allBetaJs))
print(matchingOneRep(pattern,word))

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

def oneRepDescPat(sample):
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
        if isOneRepPatternClass(canonicalForm(newAlpha))[0]:

            # next test if all words from the sample are still in the pattern language
            inSample = True
            for w in sample:
                # print(w, matchingRegular(newAlpha, w))
                if not matchingOneRep(newAlpha, w):
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

                if isOneRepPatternClass(canonicalForm(newAlpha))[0]:

                    # next test if all words from the sample are still in the pattern language
                    inSample = True
                    for w in sample:
                        # print(w, matchingRegular(newAlpha, w))
                        if not matchingOneRep(newAlpha, w):
                            inSample = False
                            break

                    if inSample:
                        alpha = newAlpha
                        q = False
                    else:
                        j += 1
            if q:
                j += 1

    return canonicalForm(alpha)


if __name__ == "__main__":

    
    # test membership
    alpha = convertToIntarray("aAbaBc")
    word1 = convertToIntarray("abcbcbcbac")
    word2 = convertToIntarray("aaa")
    #print(alpha,word1,word2)
    #print(matchingRegular(alpha, word1))
    #print(matchingRegular(alpha, word2))

    #print(matchingOneRep(alpha, word1, 46))
    #print(matchingOneRep(alpha, word2, 46))
    
    
    sample = [[1,3,3,5,3,3], [1,7,7,5,5,7,7],[1,9,9,3,5,9,9]]
    #print(descPat(sample))
    #print(oneRepDescPat(sample))
    