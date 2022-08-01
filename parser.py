import json
import time
import os

def getDisMessage(bot, channel_id, retry=3):
	res = bot.getMessages(channel_id, num=50)
	trys = 1
	while (res.status_code != 200 and trys <= retry):
		time.sleep(5)
		res = bot.getMessages(channel_id, num=50)
		trys += 1
	if res.status_code != 200:
		return False
	return res


class Parser():
	def __init__(self, bot):
		self.bot    = bot
		self.tags   = []
		self.users  = []
		self.data   = []
		self.updateData()
		self.updateTags()
		self.updateUsers()

	def updateUsers(self):
		with open('data/users.json', 'rb') as File:
			_data = File.read().decode('utf8')
			try:
				self.users = json.loads(_data)
			except Exception as e:
				print(f"ERROR {e}")
				print(f"Can't convert {_data} to json")	

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

	def save_data(self):
		# print(os.getcwd())
		with open('data/data.json', 'wb') as File:
			st = json.dumps(self.data)
			File.write(st.encode('utf8'))

	def save_tags(self):
		with open('data/tags.json', 'wb') as File:
			File.write(json.dumps(self.tags).encode('utf8'))

	def save_users(self):
		with open('data/users.json', 'wb') as File:
			File.write(json.dumps(self.users).encode('utf8'))

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

		if filter_type == 'user':
			if f"{channel_mess['author']['username']}#{channel_mess['author']['discriminator']}" in self.users:
				return True

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
			time.sleep(1)

		return {"send_mess": send_mess, "fail_log": _fail_log, "full_mess": full_mess}


