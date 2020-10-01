from console import clear
clear()
pack = "CHIPS.DAT"

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
	print(get_level())
