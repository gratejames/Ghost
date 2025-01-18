a = "dump0.hex"
b = "dump1.hex"

with open(a, "r") as f:
	a = f.read()
with open(b, "r") as f:
	b = f.read()

def hs(s):
	return "0x" + (("0" * 4) + str(hex(s))[2:])[-4:]

a = a.replace("\n", " ").split(" ")
b = b.replace("\n", " ").split(" ")

for i in range(0,0xafff):
	if a[i] != b[i]:
		print(f"${hs(i)} | A:{a[i]}, B:{b[i]}")
spa = a[0xf000]
spb = b[0xf000]
print(f"Stack Pointers: {spa}, {spb}")
for i in range(0xf001, 0xf001 + int(max(spa, spb), 16)):
	if a[i] != b[i]:
		print(f"${hs(i)} | A:{a[i]}, B:{b[i]}")
