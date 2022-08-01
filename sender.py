import json
import os

class Sender():
	def __init__(self, bot):
		self.bot     = bot
		self.chatIds = []

	def save_chatIds(self):
		with open('data/chatsIds.json', 'wb') as File:
			File.write(json.dumps(self.chatIds).encode('utf8'))

	def send_to(self, text, addr, markup=None):
		try:
			print(text)
			if not markup:
				self.bot.send_message(addr, text)
				return True
			self.bot.send_message(addr, text, reply_markup=markup)
			return True
		except Exception as e:
			print(f"ERROR {e}")
			return False

	def send_all(self, text, markup=None):
		try:
			print(text)
			for chatId in self.chatIds:
				if not markup:
					self.bot.send_message(chatId, text, disable_web_page_preview=True)
				else:	
					self.bot.send_message(chatId, text, reply_markup=markup, disable_web_page_preview=True)
			return True
		except Exception as e:
			print(f"ERROR {e}")
			return False

