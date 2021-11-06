import random
import gmpy2
from gmpy2 import mpz
import math
import sys
import os

import matplotlib.pyplot as plt

debug = False
tot_itrations = int(sys.argv[1])

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


outputBytes = int(sys.argv[1])


key = randomKeyStreamGeneration(2048)
if(debug):
    print(len(key))

output1 = pseudoRandomGeneration(outputBytes, 256, keyScheduling([], key, 256))
if(debug):
    print(len(output1))


flippingBitsArr = [i for i in range(1,33)]

rArr=[0 for i in range(32)]

xorOutputs_lis = []

for i in range(32):
    xorOutputs_lis.append([])

for i in range(tot_itrations):
    for f in flippingBitsArr:
        flippedKey = flippingKeyBits(key, f)
        output2 = pseudoRandomGeneration(outputBytes, 256, keyScheduling([], flippedKey, 256))
        
        if(debug):
            print(len(output2))
        
        xorOutputs = xor(output1,output2)
        xorOutputs_lis[f-1].append(xorOutputs)
        
        counter = frequencyCountingTestForRandomnessTesting(xorOutputs)
        D = standardDeviation(counter)
        N = len(xorOutputs)
        C = len(counter)
        rArr[f-1] += (randomness(D,C,N))

def avgLengthCalculator(output1, output2):
	val = 0
	for i in range(len(output1)):
		if output1[i] == output2[i]:
			val+=1
		else:
			break
	return val/8

def avgLengthOfIdenticalOutputVsNumberOfBitsFlipped(totalOutputBytes, numberOfRuns):
    key = randomKeyStreamGeneration(256*8)
    output1 = pseudoRandomGeneration(totalOutputBytes, 256, keyScheduling([], key, 256))
    avgLengthArr = [0 for i in range(32)]
    flippingBitsArr = [i for i in range(1,33)]
    for i in range(numberOfRuns):
        for f in flippingBitsArr:
            flippedKey = flippingKeyBits(key, f)
            output2 = pseudoRandomGeneration(totalOutputBytes, 256, keyScheduling([], flippedKey, 256))
            avgLengthArr[f-1] += avgLengthCalculator(output1, output2)
    for i in range(32):
        avgLengthArr[i] = avgLengthArr[i]/numberOfRuns
    plt.figure()
    plt.plot(flippingBitsArr, avgLengthArr)
    plt.xlabel('Number bits fliped')
    plt.ylabel('Average length in bytes of identical output')
    plt.savefig(sys.argv[2])
    plt.show()

avgLengthOfIdenticalOutputVsNumberOfBitsFlipped(1000, tot_itrations)
