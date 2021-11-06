import random
import gmpy2
from gmpy2 import mpz
import math
import sys
import os

import matplotlib.pyplot as plt

debug = True
tot_itrations = int(sys.argv[2])

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

for i in range(33):
    xorOutputs_lis.append([])
    
xorOutputs_lis[0].append(output1)

for i in range(tot_itrations):
    for f in flippingBitsArr:
        flippedKey = flippingKeyBits(key, f)
        output2 = pseudoRandomGeneration(outputBytes, 256, keyScheduling([], flippedKey, 256))
        
        if(debug):
            print(len(output2))
        
        xorOutputs = xor(output1,output2)
        xorOutputs_lis[f].append(output2)
        
        counter = frequencyCountingTestForRandomnessTesting(xorOutputs)
        D = standardDeviation(counter)
        N = len(xorOutputs)
        C = len(counter)
        rArr[f-1] += (randomness(D,C,N))

# checking the number of bits are similar
for i in range(len(xorOutputs_lis)):
    sm = 0
    for j in range(1,len(xorOutputs_lis[0])):
        
        if(debug):
            print(xorOutputs_lis[i][0])
            print(xorOutputs_lis[i][j])
        sm+=count_ones(xorOutputs_lis[i][0],xorOutputs_lis[i][j])
    print(sm/(len(xorOutputs_lis[0])-1))


for i in range(32):
	rArr[i]=rArr[i]/tot_itrations

print(rArr)

x_axis=[]
for i in range(1,33):
    x_axis.append(i)
# plotting
#plt.figure(figsize=(10,10))
plt.figure()
plt.plot(x_axis,rArr)

plt.xlabel('Number of bits filpped')
plt.ylabel('R')

#plt.savefig("plot_"+str(outputBytes)+"_"+str(tot_itrations)+".png")
plt.savefig(sys.argv[3])

if (debug):
    plt.show()
