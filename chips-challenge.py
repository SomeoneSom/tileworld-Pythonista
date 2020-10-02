from console import clear
from scene import *
clear()
pack = "CHIPS.DAT"
sheet = Texture("img/IMG_1212.PNG")
x = 1/7
y = 1/16
xm = -1
ym = 16
off = 1/sheet.size[0]
textures = {}
for a in range(112):
	temp = ym - (a % 16)
	if a % 16 == 0:
		xm += 1
	textures[a] = sheet.subtexture((x*xm, y*temp, x, -y))

#unsigned words are reversed, very weird so this fixes that
def fix(word_list):
	words = [word_list[i:i+2] for i in range(0, len(word_list), 2)]
	temp = []
	fixed = ""
	for word in words:
		temp.insert(0, word)
		if len(temp) == 2:
			for t in temp:
				fixed += t
			temp = []
	return fixed

#main code start
with open(pack, "rb") as f:
	
	#checks for a correct header
	header = f.read(4).hex()
	if not (header == "0002aaac" or header == "acaa0200"):
		print("Error: Not a valid Chips Challenge level pack! (broken header or header implies Lynx rules)")
	level_count = int(fix(f.read(2).hex()), 16)
	level_number = 1
	
	#gets ASCII data from a zero terminated string
	def get_string():
		byte = f.read(1).hex()
		string = ""
		while byte != "00":
			string += chr(int(byte, 16))
			byte = f.read(1).hex()
		return string
	
	#gets the data of a level
	def get_level():
		layer1 = []
		layer2 = []
		row = []
		traps = []
		movement = []
		cloners = []
		map_title = ""
		password = ""
		hint_text = ""
		f.read(4)
		time_lim = int(fix(f.read(2).hex()), 16)
		chip_count = int(fix(f.read(2).hex()), 16)
		f.read(2)
		byte_count = int(fix(f.read(2).hex()), 16)
		raw_data = f.read(byte_count).hex()
		data = [raw_data[i:i+2] for i in range(0, len(raw_data), 2)]
		flag = 0
		copies = 0
		for byte in data:
			if byte == "ff" and flag == 0:
				flag = 3
			if flag == 2:
				copies = int(byte, 16)
			elif flag == 1:
				for x in range(copies):
					row.append(int(byte, 16))
			elif flag != 3:
				row.append(int(byte, 16))
			if len(row) == 32:
				layer1.append(row)
				row = []
			elif len(row) > 32:
				while len(row) >= 32:
					layer1.append(row[0:32])
					row = row[32:]
			if flag > 0:
				flag -= 1
		byte_count = int(fix(f.read(2).hex()), 16)
		raw_data = f.read(byte_count).hex()
		data = [raw_data[i:i+2] for i in range(0, len(raw_data), 2)]
		flag = 0
		copies = 0
		for byte in data:
			if byte == "ff" and flag == 0:
				flag = 3
			elif flag == 2:
				copies = int(byte, 16)
			elif flag == 1:
				for x in range(copies):
					row.append(int(byte, 16))
			elif flag != 3:
				row.append(int(byte, 16))
			if len(row) == 32:
				layer2.append(row)
				row = []
			elif len(row) > 32:
				while len(row) >= 32:
					layer2.append(row[0:32])
					row = row[32:]
			if flag > 0:
				flag -= 1
		main_byte_count = int(fix(f.read(2).hex()), 16)
		#print(main_byte_count)
		#print(f.read(main_byte_count).hex())
		while main_byte_count > 3:
			type = int(f.read(1).hex(), 16)
			main_byte_count -= 1
			if type == 3:
				offset = int(f.read(1).hex(), 16)
				map_title = get_string()
			elif type == 4:
				offset = int(f.read(1).hex(), 16) * 10
				temp = offset / 10
				while temp > 0:
					data = [int(fix(f.read(2).hex()), 16), int(fix(f.read(2).hex()), 16), int(fix(f.read(2).hex()), 16), int(fix(f.read(2).hex()), 16)]
					traps.append(data)
					f.read(2)
					temp -= 1
			elif type == 5:
				offset = int(f.read(1).hex(), 16) * 8
				temp = offset / 8
				while temp > 0:
					data = [int(fix(f.read(2).hex()), 16), int(fix(f.read(2).hex()), 16), int(fix(f.read(2).hex()), 16), int(fix(f.read(2).hex()), 16)]
					cloners.append(data)
					temp -= 1
			elif type == 6:
				offset = int(f.read(1).hex(), 16)
				encoded = get_string()
				for char in encoded:
					password += chr(ord(char) ^ 153)
			elif type == 7:
				offset = int(f.read(1).hex(), 16)
				hint_text = get_string()
			elif type == 10:
				offset = int(f.read(1).hex(), 16) * 2
				temp = offset / 2
				while temp > 0:
					data = [int(f.read(1).hex(), 16), int(f.read(1).hex(), 16)]
					movement.append(data)
					temp -= 1
			else:
				print("Error: Invalid Optional Field")
				break
			main_byte_count -= offset
		return [layer1, layer2, traps, movement, cloners, map_title, password, hint_text, time_lim, chip_count]
		
	#main code
	class Game (Scene):
		
		def setup(self):
			self.background_color = "#000000"
			self.tile_size = (self.size[1] / 9)
			self.layer1, self.layer2, self.traps, self.movement, self.cloners, self.map_title, self.password, hint_texta, self.time_lim, self.chip_count = get_level()
			temp = 0
			self.hint_text = ""
			for char in hint_texta:
				if temp >= 15 and char == " ":
					self.hint_text += "\n"
					temp = -1
				self.hint_text += char
				temp += 1
			self.curr_time = self.time_lim
			self.curr_chips = self.chip_count
			self.display_hint = False
			self.level = 1
			self.pos = []
			for row in self.layer1:
				if int("6e", 16) in row:
					self.pos = [self.layer1.index(row), row.index(int("6e", 16))]
			self.draw()
			
		def draw(self):
			for child in self.children:
				child.remove_from_parent()
			to_draw1 = []
			to_draw2 = []
			for y in range(4, -5, -1):
				for x in range(-4, 5):
					try:
						to_draw1.append(self.layer1[self.pos[0]-y][self.pos[1]+x])
					except:
						to_draw1.append(0)
					try:
						to_draw2.append(self.layer2[self.pos[0]-y][self.pos[1]+x])
					except:
						to_draw2.append(0)
			count = 0
			for y in range(9, 0, -1):
				for x in range(1, 10):
					self.add_child(SpriteNode(textures[to_draw2[count]], position = ((self.tile_size * x) - self.tile_size / 2, (self.tile_size * y) - self.tile_size / 2), size = (self.tile_size, self.tile_size)))
					self.add_child(SpriteNode(textures[to_draw1[count]], position = ((self.tile_size * x) - self.tile_size / 2, (self.tile_size * y) - self.tile_size / 2), size = (self.tile_size, self.tile_size)))
					count += 1
			self.add_child(LabelNode("Time: " + str(self.curr_time), position = (self.tile_size * 10.5, self.size[1] - self.tile_size)))
			self.add_child(LabelNode("Chips: " + str(self.curr_chips), position = (self.tile_size * 10.5, self.size[1] - self.tile_size * 2)))
			self.add_child(LabelNode("Level " + str(self.level) + ": " + self.map_title, position = (self.tile_size * 10.5, self.size[1] - self.tile_size * 3)))
			self.add_child(LabelNode("Password: " + self.password, position = (self.tile_size * 10.5, self.size[1] - self.tile_size * 4)))
			if self.display_hint:
				self.add_child(LabelNode(self.hint_text, font = ("Helvetica", 20), position = (self.tile_size * 10.5, self.size[1] - self.tile_size * 5)))
				
		def update(self):
			pass
			
	run(Game(), LANDSCAPE)
