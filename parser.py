import json
import time

def getDisMessage(bot, channel_id, retry=3):
	res = bot.getMessages(channel_id, num=50)
	trys = 1
	while (res.status_code != 200 and trys <= retry):
		res = bot.getMessages(channel_id, num=50)
		trys += 1
	if res.status_code != 200:
		return False
	return res


class Parser():
	def __init__(self, bot):
		self.bot    = bot
		self.tags   = []
		self.data   = []
		self.updateData()
		self.updateTags()

	def updateTags(self):
		with open('data/tags.json', 'rb') as File:
			_data = File.read().decode('utf8')
			try:
				self.tags = json.loads(_data)
			except Exception as e:
				print(f"ERROR {e}")
				print(f"Can't convert {_data} to json")	
		
		


	def updateData(self):
		with open('data/data.json', 'rb') as File:
			_data = File.read().decode('utf8')
			try:
				self.data = json.loads(_data)
			except Exception as e:
				print(f"ERROR {e}")
				print(f"Can't convert {_data} to json")
				
		File_add = open('data/add.json', 'rb')
		File_remove = open('data/remove.json', 'rb')
		_data_add = File_add.read().decode('utf8')
		_data_remove = File_remove.read().decode('utf8')
		try:
			data_add = json.loads(_data_add)
			data_remove = json.loads(_data_remove)
		except Exception as e:
			print(f"ERROR {e}")
			print(f"Can't convert add or remove file to json")

		for channel in data_add:
			if channel['channel_id'] not in [i['channel_id'] for i in self.data]:
				self.data.append(channel)

		for channel in data_remove:
			for i in range(len(self.data)):
				if channel['channel_id'] == self.data[i]['channel_id']:
					del(self.data[i])

		File_add.close()
		File_remove.close()

		File_add = open('data/add.json', 'w')
		File_remove = open('data/remove.json', 'w')
		File_add.write("[]")
		File_remove.write("[]")
		File_add.close()
		File_remove.close()
		self.save_data()

	def save_data(self):
		with open('data/data.json', 'wb') as File:
			File.write(json.dumps(self.data).encode('utf8'))

	def save_tags(self):
		with open('data/tags.json', 'wb') as File:
			File.write(json.dumps(self.tags).encode('utf8'))


	def filter(self, channel_mess, filter_type, channel_data):
		if filter_type == 'tags':
			for tag in self.tags:
				if tag in channel_mess['content']:
					return True

		if filter_type == 'role':
			roles = self.bot.getProfile(channel_mess['author']['id'], guildID=channel_data['informatin'].split('/')[:-2][0])
			if roles.status_code != 200:
				return False
			for role in roles.json()['guild_member']['roles']:
				if role in channel_data['roles']:
					return True
			time.sleep(1)

		return False

	def parse_mess(self, retry=3):
		send_mess = []
		full_mess = []
		_fail_log = []
		for channel_mess in self.data:
			res = getDisMessage(self.bot, channel_mess['channel_id'])
			if not res:
				_fail_log.append(channel_mess)
				continue
			res = res.json()
			for key in channel_mess.keys():
				if key not in res[0]:
					res[0][key] = channel_mess[key]

			full_mess.append(res[0])
			# print(res[0])
			if channel_mess['timestamp'] != res[0]['timestamp']:
				start_index = 0
				while start_index < 50 and channel_mess['timestamp'] != res[start_index]['timestamp']:
					start_index += 1
				start_index -= 1
				# print(start_index)
				while start_index >= 0:
					if self.filter(res[start_index], channel_mess['filter_type'], channel_mess):
						for key in channel_mess.keys():
							if key not in res[start_index]:
								res[start_index][key] = channel_mess[key]
						send_mess.append(res[start_index])
					start_index -= 1

		return {"send_mess": send_mess, "fail_log": _fail_log, "full_mess": full_mess}


