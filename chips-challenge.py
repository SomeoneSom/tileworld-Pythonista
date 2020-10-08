from console import clear
from scene import *
from time import sleep as delay
from copy import deepcopy
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
	f.close()
		
#main code
class Game (Scene):
	
	def get_level(self, level):
		with open(pack, "rb") as f:
			def get_string():
				byte = f.read(1).hex()
				string = ""
				while byte != "00":
					string += chr(int(byte, 16))
					byte = f.read(1).hex()
				return string
			f.read(6)
			t = level - 1
			while t != 0:
				f.read(int(fix(f.read(2).hex()),16))
				t -= 1
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
					temp = offset / 4
					while temp > 0:
						data = [int(f.read(1).hex(), 16), int(f.read(1).hex(), 16)]
						movement.append(data)
						temp -= 1
				else:
					print("Error: Invalid Optional Field")
					break
				main_byte_count -= offset
			return [layer1, layer2, traps, movement, cloners, map_title, password, hint_text, time_lim, chip_count]
		
	def setup(self):
		self.background_color = "#000000"
		self.tile_size = (self.size[1] / 9)
		self.layer1, self.layer2, self.traps, self.movement, self.cloners, self.map_title, self.password, hint_texta, self.time_lim, self.chip_count = self.get_level(1)
		self.back1 = deepcopy(self.layer1)
		self.back2 = deepcopy(self.layer2)
		self.backm = deepcopy(self.movement)
		temp = 0
		self.hint_text = ""
		for char in hint_texta:
			if temp >= 25 and char == " ":
				self.hint_text += "\n"
				temp = -1
			self.hint_text += char
			temp += 1
		self.curr_time = self.time_lim
		self.curr_chips = self.chip_count
		self.display_hint = False
		self.keys = [0, 0, False, 0]
		self.shields = [False, False, False, False]
		self.move = [False, False, False, False]
		self.direction = 0
		self.tick = 0
		self.started = False
		self.level = 1
		self.pos = []
		self.ready = True
		self.un_hold = True
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
				if x == 0 and y == 0:
					to_draw1.append(110 + self.direction)
				else:
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
		if self.keys[0] > 0:
			self.add_child(SpriteNode(textures[100], position = ((self.tile_size * 10) - self.tile_size / 2, (self.tile_size * 2) - self.tile_size / 2), size = (self.tile_size, self.tile_size)))
		if self.keys[1] > 0:
			self.add_child(SpriteNode(textures[101], position = ((self.tile_size * 11) - self.tile_size / 2, (self.tile_size * 2) - self.tile_size / 2), size = (self.tile_size, self.tile_size)))
		if self.keys[2]:
			self.add_child(SpriteNode(textures[102], position = ((self.tile_size * 10) - self.tile_size / 2, (self.tile_size) - self.tile_size / 2), size = (self.tile_size, self.tile_size)))
		if self.keys[3] > 0:
			self.add_child(SpriteNode(textures[103], position = ((self.tile_size * 11) - self.tile_size / 2, (self.tile_size) - self.tile_size / 2), size = (self.tile_size, self.tile_size)))
		self.add_child(LabelNode("Time: " + str(self.curr_time), position = (self.tile_size * 10.5, self.size[1] - self.tile_size)))
		self.add_child(LabelNode("Chips: " + str(self.curr_chips), position = (self.tile_size * 10.5, self.size[1] - self.tile_size * 2)))
		self.add_child(LabelNode("Level " + str(self.level) + ": " + self.map_title, position = (self.tile_size * 10.5, self.size[1] - self.tile_size * 3)))
		self.add_child(LabelNode("Password: " + self.password, position = (self.tile_size * 10.5, self.size[1] - self.tile_size * 4)))
		if self.display_hint:
			self.add_child(LabelNode(self.hint_text, font = ("Helvetica", 20), position = (self.tile_size * 10.5, self.size[1] - self.tile_size * 5)))
			
	def update(self):
		if self.started:
			delay(0.05)
			self.tick = self.tick % 20
			if self.tick % 4 == 0:
				self.update_board_monstfast()
				self.ready = True
			if self.ready and True in self.move:
				self.update_board_player([int(self.move[2])-int(self.move[0]), int(self.move[1])-int(self.move[3])])
				self.direction = 0+int(self.move[1])-int(self.move[3])-2*int(self.move[0])
				self.ready = False
			if self.un_hold:
				for a in range(0, 4):
					self.move[a] = False
			self.tick += 1
			if self.tick == 20:
				self.curr_time -= 1	
		
	def touch_began(self, touch):
		if not self.started:
			self.started = True
		if True not in self.move:
			if touch.location[1] > self.size[1] - 50:
				self.move[0] = True
			elif touch.location[0] > self.size[0] - 50:
				self.move[1] = True
			elif touch.location[1] < 50:
				self.move[2] = True
			elif touch.location[0] < 50:
				self.move[3] = True	
				
	def touch_ended(self, touch):
		self.un_hold = True
			
	def update_board_player(self, offset):
		next = self.layer1[self.pos[0] + offset[0]][self.pos[1] + offset[1]]
		curr = self.layer1[self.pos[0]][self.pos[1]]
		repl = self.layer2[self.pos[0]][self.pos[1]]
		next2 = self.layer1[self.pos[0] + offset[0]*2][self.pos[1] + offset[1]*2]
		self.display_hint = False
		if repl == 47:
			self.display_hint = True
		if next == 0:
			self.layer1[self.pos[0]][self.pos[1]] = repl
			self.layer2[self.pos[0]][self.pos[1]] = 0
			self.layer1[self.pos[0] + offset[0]][self.pos[1] + offset[1]] = curr
			self.pos[0] += offset[0]
			self.pos[1] += offset[1]
		elif next == 1:
			pass
		elif next == 2:
			self.layer1[self.pos[0]][self.pos[1]] = repl
			self.layer2[self.pos[0]][self.pos[1]] = 0
			self.layer1[self.pos[0] + offset[0]][self.pos[1] + offset[1]] = curr
			self.pos[0] += offset[0]
			self.pos[1] += offset[1]
			self.curr_chips -= 1
		elif next == 3:
			if self.shields[0]:
				self.layer1[self.pos[0]][self.pos[1]] = repl
				self.layer2[self.pos[0]][self.pos[1]] = 0
				self.layer1[self.pos[0] + offset[0]][self.pos[1] + offset[1]] = curr
				self.pos[0] += offset[0]
				self.pos[1] += offset[1]
			else:
				self.reset()
		elif next == 10:
			can_move = False
			if next2 == 0:
				can_move = True
			elif next2 == 3:
				self.layer1[self.pos[0] + offset[0]*2][self.pos[1] + offset[1]*2] = 11
				self.layer1[self.pos[0]][self.pos[1]] = repl
				self.layer2[self.pos[0]][self.pos[1]] = 0
				self.layer1[self.pos[0] + offset[0]][self.pos[1] + offset[1]] = curr
				self.pos[0] += offset[0]
				self.pos[1] += offset[1]
			if can_move:
				self.layer1[self.pos[0] + offset[0]*2][self.pos[1] + offset[1]*2] = 10
				self.layer1[self.pos[0]][self.pos[1]] = repl
				self.layer2[self.pos[0]][self.pos[1]] = 0
				self.layer1[self.pos[0] + offset[0]][self.pos[1] + offset[1]] = curr
				self.pos[0] += offset[0]
				self.pos[1] += offset[1]
		elif next == 11:
			self.layer1[self.pos[0]][self.pos[1]] = repl
			self.layer2[self.pos[0]][self.pos[1]] = 0
			self.layer1[self.pos[0] + offset[0]][self.pos[1] + offset[1]] = curr
			self.layer2[self.pos[0] + offset[0]][self.pos[1] + offset[1]] = 0
			self.pos[0] += offset[0]
			self.pos[1] += offset[1]
		elif next == 21:
			self.change_level()
		elif next == 22 and self.keys[0] >= 1:
			self.layer1[self.pos[0]][self.pos[1]] = repl
			self.layer2[self.pos[0]][self.pos[1]] = 0
			self.layer1[self.pos[0] + offset[0]][self.pos[1] + offset[1]] = curr
			self.pos[0] += offset[0]
			self.pos[1] += offset[1]
			self.keys[0] -= 1
		elif next == 23 and self.keys[1] >= 1:
			self.layer1[self.pos[0]][self.pos[1]] = repl
			self.layer2[self.pos[0]][self.pos[1]] = 0
			self.layer1[self.pos[0] + offset[0]][self.pos[1] + offset[1]] = curr
			self.pos[0] += offset[0]
			self.pos[1] += offset[1]
			self.keys[1] -= 1
		elif next == 24 and self.keys[2]:
			self.layer1[self.pos[0]][self.pos[1]] = repl
			self.layer2[self.pos[0]][self.pos[1]] = 0
			self.layer1[self.pos[0] + offset[0]][self.pos[1] + offset[1]] = curr
			self.pos[0] += offset[0]
			self.pos[1] += offset[1]
		elif next == 25 and self.keys[3] >= 1:
			self.layer1[self.pos[0]][self.pos[1]] = repl
			self.layer2[self.pos[0]][self.pos[1]] = 0
			self.layer1[self.pos[0] + offset[0]][self.pos[1] + offset[1]] = curr
			self.pos[0] += offset[0]
			self.pos[1] += offset[1]
			self.keys[3] -= 1
		elif next == 34 and self.curr_chips == 0:
			self.layer1[self.pos[0]][self.pos[1]] = repl
			self.layer2[self.pos[0]][self.pos[1]] = 0
			self.layer1[self.pos[0] + offset[0]][self.pos[1] + offset[1]] = curr
			self.pos[0] += offset[0]
			self.pos[1] += offset[1]
		elif next == 47:
			self.layer1[self.pos[0]][self.pos[1]] = repl
			self.layer2[self.pos[0]][self.pos[1]] = 0
			self.layer1[self.pos[0] + offset[0]][self.pos[1] + offset[1]] = curr
			self.layer2[self.pos[0] + offset[0]][self.pos[1] + offset[1]] = 47
			self.pos[0] += offset[0]
			self.pos[1] += offset[1]
			self.display_hint = True
		elif next == 100:
			self.layer1[self.pos[0]][self.pos[1]] = repl
			self.layer2[self.pos[0]][self.pos[1]] = 0
			self.layer1[self.pos[0] + offset[0]][self.pos[1] + offset[1]] = curr
			self.pos[0] += offset[0]
			self.pos[1] += offset[1]
			self.keys[0] += 1
		elif next == 101:
			self.layer1[self.pos[0]][self.pos[1]] = repl
			self.layer2[self.pos[0]][self.pos[1]] = 0
			self.layer1[self.pos[0] + offset[0]][self.pos[1] + offset[1]] = curr
			self.pos[0] += offset[0]
			self.pos[1] += offset[1]
			self.keys[1] += 1
		elif next == 102:
			self.layer1[self.pos[0]][self.pos[1]] = repl
			self.layer2[self.pos[0]][self.pos[1]] = 0
			self.layer1[self.pos[0] + offset[0]][self.pos[1] + offset[1]] = curr
			self.pos[0] += offset[0]
			self.pos[1] += offset[1]
			self.keys[2] = True
		elif next == 103:
			self.layer1[self.pos[0]][self.pos[1]] = repl
			self.layer2[self.pos[0]][self.pos[1]] = 0
			self.layer1[self.pos[0] + offset[0]][self.pos[1] + offset[1]] = curr
			self.pos[0] += offset[0]
			self.pos[1] += offset[1]
			self.keys[3] += 1
			
	def update_board_monstfast(self):
		g = 0
		for pos in self.movement:
			curr = self.layer1[pos[1]][pos[0]]
			repl = self.layer2[pos[1]][pos[0]]
			acting = [11, 47, 21, 10, 46, 2, 34, 33, 50, 1]
			for a in range(64, 100):
				acting.append(a)
			for a in range(22, 26):
				acting.append(a)
			for a in range(104, 108):
				acting.append(a)
			offset = [0, 0]
			if curr >= 64 and curr <= 67:
				acting.append(4)
				try:
					left = self.layer1[pos[1]+int(curr == 65)-int(curr == 67)][pos[0]+int(curr == 66)-int(curr == 64)]
					if left in acting:
						offset = [int(curr == 66)-int(curr == 64), int(curr == 67)-int(curr == 65)]
					else:
						self.layer1[pos[1]][pos[0]] = ((curr - 64) + 1 % 4) + 64
						curr = (((curr - 64) + 1) % 4) + 64
						offset = [int(curr == 66)-int(curr == 64), int(curr == 67)-int(curr == 65)]
				except:
					offset = [int(curr == 66)-int(curr == 64), int(curr == 67)-int(curr == 65)]
				next = self.layer1[pos[1] + offset[0]][pos[0] + offset[1]]
				if next in acting:
					temp = 0
					a = 0
					while temp not in acting and a != 4:
						curr = (((curr - 64) - 1) % 4)
						if curr < 0:
							curr = 3
						curr += 64
						offset = [int(curr == 66)-int(curr == 64), int(curr == 67)-int(curr == 65)]
						temp = self.layer1[pos[1]+int(curr == 65)-int(curr == 67)][pos[0]+int(curr == 66)-int(curr == 64)]
						a += 1
					if a == 4:
						offset = [0, 0]
					next = self.layer1[pos[1] + offset[0]][pos[0] + offset[1]]
				if next == 3:
					self.layer1[pos[1]][pos[0]] = repl
					self.layer2[pos[1]][pos[0]] = 0
					self.movement.remove(pos)
				else:
					offset = [int(curr == 66)-int(curr == 64), int(curr == 67)-int(curr == 65)]
					self.layer1[pos[1]][pos[0]] = repl
					self.layer2[pos[1]][pos[0]] = 0
					self.layer2[pos[1] + offset[0]][pos[0] + offset[1]] = self.layer1[pos[1] + offset[0]][pos[0] + offset[1]]
					self.layer1[pos[1] + offset[0]][pos[0] + offset[1]] = curr
					self.movement[g][0] += offset[1]
					self.movement[g][1] += offset[0]
					temp = deepcopy(self.movement[g])
					temp.reverse()
					if temp == self.pos:
						self.reset()
						return
			g += 1
			
	def reset(self):
		self.layer1 = self.back1
		self.layer2 = self.back2
		self.back1 = deepcopy(self.layer1)
		self.back2 = deepcopy(self.layer2)
		self.curr_time = self.time_lim
		self.curr_chips = self.chip_count
		self.movement = self.backm
		self.backm = deepcopy(self.movement)
		self.display_hint = False
		self.keys = [0, 0, False, 0]
		self.move = [False, False, False, False]
		self.shields = [False, False, False, False]
		self.tick = 0
		self.started = False
		self.pos = []
		for row in self.layer1:
			if int("6e", 16) in row:
				self.pos = [self.layer1.index(row), row.index(int("6e", 16))]
		self.draw()
		
	def change_level(self):
		self.level += 1
		self.layer1, self.layer2, self.traps, self.movement, self.cloners, self.map_title, self.password, hint_texta, self.time_lim, self.chip_count = self.get_level(self.level)
		self.back1 = deepcopy(self.layer1)
		self.back2 = deepcopy(self.layer2)
		self.backm = deepcopy(self.movement)
		temp = 0
		self.hint_text = ""
		for char in hint_texta:
			if temp >= 25 and char == " ":
				self.hint_text += "\n"
				temp = -1
			self.hint_text += char
			temp += 1
		self.curr_time = self.time_lim
		self.curr_chips = self.chip_count
		self.display_hint = False
		self.keys = [0, 0, False, 0]
		self.shields = [False, False, False, False]
		self.move = [False, False, False, False]
		self.tick = 0
		self.started = False
		self.pos = []
		for row in self.layer1:
			if int("6e", 16) in row:
				self.pos = [self.layer1.index(row), row.index(int("6e", 16))]
		self.draw()
			
run(Game(), LANDSCAPE)