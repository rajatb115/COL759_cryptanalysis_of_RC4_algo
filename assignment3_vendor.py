import random
import gmpy2
from gmpy2 import mpz
import math
import sys
import os

import matplotlib.pyplot as plt

debug = False
#tot_itrations = int(sys.argv[1])



# Key scheduling function
def keyScheduling(S,key,sBytes):
    key1=[]
    
    # converting the key into 8bit stream (byte stream)
    for i in range(len(key)//8):
        key1.append(int(key[8*i:8*(i+1)],2))
    
    # initializing S
    for i in range(sBytes):
        S.append(i)
    j=0
    for i in range(sBytes):
        j = (j+S[i]+key1[i%len(key1)])%sBytes
        temp = S[i]
        S[i] = S[j]
        S[j] = temp
    return S

# pseudo random generation function
def pseudoRandomGeneration(numberOfOutputs,sBytes,S):
	i = 0
	j = 0
	output=""
	while(numberOfOutputs>0):
		i = (i+1)%sBytes
		j = (j+S[i])%sBytes
		temp = S[i]
		S[i] = S[j]
		S[j] = temp
		val = bin(S[(S[i]+S[j])%sBytes]).replace("0b","")
		output += (8-len(val))*"0" + val
		numberOfOutputs -= 1
	return output

def xor(a,b):
	ans = ""
	for i in range(len(a)):
		if(a[i]==b[i]):
			ans+="0"
		else:
			ans+="1"
	return ans

def randomKeyStreamGeneration(numberOfBits):
	decimal = random.randint(mpz(2)**(numberOfBits-1),mpz(2)**numberOfBits -1)
	return bin(decimal).replace("0b","")

def flippingKeyBits(key,numberOfBitsToFlip):
	randomIndicesList = random.sample(range(0, len(key)-1), numberOfBitsToFlip)
	for i in randomIndicesList:
		key = key[:i] + str(abs(int(key[i])-1)) + key[i+1:]
	return key

def frequencyCountingTestForRandomnessTesting(testData):
	counter = {}
	for i in range(256):
		counter[i] = 0
	for i in range(len(testData)-8+1):
		counter[int(testData[i:i+8],2)] += 1
	return counter

def standardDeviation(counter):
	mean = 0
	for c in counter:
		mean += counter[c]
	mean = mean/len(counter)
	dev = 0
	for c in counter:
		dev += (counter[c]-mean)**2
	dev = dev/len(counter)
	dev = math.sqrt(dev)
	return dev

def randomness(D,C,N):
	return (D*C)/N

def count_ones(output1, output2):
    cnt = 0 
    for i in range(len(output1)):
        if(output1[i]!=output2[i]):
            cnt+=1
    return cnt
    
def vendorPart(vendorMessageLengthInBytes, maximumOutputToThrowForAnalysis, numberOfRuns):
    avgRandomnessArr = [0 for i in range(maximumOutputToThrowForAnalysis)]
    key = randomKeyStreamGeneration(256*8)
    for i in range(numberOfRuns):
        outputKeyStream = pseudoRandomGeneration(maximumOutputToThrowForAnalysis+vendorMessageLengthInBytes, 256, keyScheduling([], key, 256))
        for i in range(maximumOutputToThrowForAnalysis):
            output = outputKeyStream[i*8:i*8+vendorMessageLengthInBytes*8]
            counter = frequencyCountingTestForRandomnessTesting(output)
            D = standardDeviation(counter)
            N = len(output)
            C = len(counter)
            avgRandomnessArr[i] += randomness(D,C,N)
    for i in range(maximumOutputToThrowForAnalysis):
        avgRandomnessArr[i] = avgRandomnessArr[i]/numberOfRuns
    x= [i for i in range(maximumOutputToThrowForAnalysis)]
    plt.figure()
    plt.xlabel('Initial Output to throw')
    plt.ylabel('R')
    plt.plot(x,avgRandomnessArr)
    
    plt.savefig(sys.argv[2])
    
    plt.show()
    numberOfOutputsWeShouldThrowForMinRandomness = avgRandomnessArr.index(min(avgRandomnessArr))
    return numberOfOutputsWeShouldThrowForMinRandomness

maximumOutputToThrowForAnalysis = 2560
vendorMessageLengthInBytes = 50
numberOfRuns = int(sys.argv[1])
print(vendorPart(vendorMessageLengthInBytes, maximumOutputToThrowForAnalysis, numberOfRuns))
