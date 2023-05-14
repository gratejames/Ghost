def badDefinitions(message):
	print(f"badDefinitions: {message}")

def addTuples(t1, t2):
	return (t1[0]+t2[0], t1[1]+t2[1])

def twosComp(val, bits=8): # https://stackoverflow.com/questions/1604464/twos-complement-in-python
	if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
		val = val - (1 << bits)        # compute negative value
	return val                         # return positive value as is

def bitNOT(num):
	return int(str(bin(int(~np.uint8(num))))[4:],2)

# rrrrr gggggg bbbbb
def binColor(num):
	return (num // 2048 * (255 / 31), (num % 2048) // 32 * (255 / 63), (num % 32) * (255 / 31))
	print(color)

def Lmap(v, a1,b1,a2,b2, cap = True):
	x = a2 + (b2-a2)*((v-a1)/(b1-a1))
	return int(x) if not cap or x <= b2 else int(b2)
	# real value if it's good or it's not capped

def ForceValidInt(x):
	while x < 0:
		x += 0xffff
	return x%0x10000

def Pretty(hexInt):
	return "0x"+str(hex(hexInt))[2:].zfill(4)