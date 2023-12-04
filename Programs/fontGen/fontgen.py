import pygame
import json

pygame.init()
  
window = pygame.display.set_mode((800, 850))
window.fill((255, 255, 255))
pygame.display.set_caption("GHASM Font Creator")

font = pygame.freetype.Font('Anonymous_Pro_B.ttf')
font.antialiased = False
ticker = pygame.time.Clock()
done = False

storedFonts = {}
fontId = ord('a')

def setupID(fid):
	storedFonts[fid] = [0x0000,0x0000,0x0000,0x0000]

def toggleID(fid, x, y):
	byte = y//2
	# print("byte", byte)
	storedFonts[fid][byte] = (storedFonts[fid][byte] ^ (0x8000 >> x+(y%2*8))) % 0x10000
	# print("\n".join([str(bin(byte)).replace("0b", "").zfill(16) for byte in storedFonts[fid]]))

def getID(fid, x, y):
	byte = y//2
	return (storedFonts[fid][byte] & (0x8000 >> x+(y%2*8))) % 0x10000

def saveFont(export=False):
	with open("fontFile.json", "w+") as f:
		f.write(json.dumps(storedFonts))
	print("Saved!")
	if not export:
		return
	with open("font.hex", "w+") as f:
		output = []
		for char in range(ord(' '), ord('~')):
			output.append(" ".join(    [("0x" + str(hex(byte)).replace("0x", "").zfill(4)) for byte in storedFonts.get(char, [0x0000,0x0000,0x0000,0x0000])]    ))
		f.write("\n".join(output))
	
def loadFont():
	with open("fontFile.json", "r") as f:
		loadedFont = json.loads(f.read())
	
	for k,v in loadedFont.items():
		storedFonts[int(k)] = v
	print("Loaded!")
	print(storedFonts)
	print("!Loaded")
		
loadFont()
while not done:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done = True
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_s:
				saveFont()
			if event.key == pygame.K_e:
				saveFont(export=True)
				
			if event.key == pygame.K_l:
				loadFont()
				
			if event.key == pygame.K_LEFT:
				saveFont()
				fontId-=1
			if event.key == pygame.K_RIGHT:
				saveFont()
				fontId+=1
				
			
				
		if event.type == pygame.MOUSEBUTTONDOWN:
			x,y = pygame.mouse.get_pos()
			if y < 50:
				continue
			y -= 50
			x //= 100
			y //= 100
			# print(x,y)
			toggleID(fontId, x, y)
	
	if not fontId in storedFonts.keys():
		setupID(fontId)
		
	window.fill((255, 255, 255))
	font.render_to(window, (10,10), 'Current character: '+ chr(fontId), (0, 0, 0),size=40)
	
	for row in range(8):
		for i in range(8):
			color = (0,0,0) if getID(fontId, i, row) else (230,230,230)
			outline = (255,200,200) if i==0 or row==0 else (255,230,200) if i in [1,2] else (255,255,255)
			pygame.draw.rect(window,   color, (i*100, 50+row*100, 100, 100), 0)
			pygame.draw.rect(window, outline, (i*100, 50+row*100, 100, 100), 3)
	
	pygame.display.update()
	ticker.tick(30)