import parser
import telebot
import discum
import json
import time
import utils
import threading

from sender import Sender
from telebot import types


with open('config.json', 'rb') as File:
	cfg = json.loads(File.read().decode('utf8'))
	tg_bot = telebot.TeleBot(cfg['tg_token'])
	disBot = discum.Client(token=cfg['distoken'], log=False)

	sender = Sender(tg_bot)
	pars = parser.Parser(disBot)
	sender.chatIds = cfg['chatIds']

with open('data/acc_info.json', 'rb') as File:
	acc_info = json.loads(File.read().decode('utf8'))

@tg_bot.message_handler(commands=['start'])
def com_start(msg):
	if msg.chat.id not in sender.chatIds:
		tg_bot.send_message(msg.chat.id, "Hello, it't bot not for you!")
		return

	tg_bot.send_message(msg.chat.id, f"Hello\n\nHow to use:\nSend link to chat(example: https://discord.com/channels/965966609078448138/965966609330077701)\nOR you can send just chat(example: 965966609330077701)\n\nFor add tag use '+'(example: +hello)\nFor delite tag use '-'(example: -hello)\nFor show tags: tags\nYou'r sender.chatIds: {msg.chat.id}", disable_web_page_preview=True)

@tg_bot.message_handler(commands=['help'])
def helper(msg):
	if msg.chat.id not in sender.chatIds:
		tg_bot.send_message(msg.chat.id, "Hello, it't bot not for you!")
		return
	tg_bot.send_message(msg.chat.id, 'Little help\nadd channel: channel_id(or link to channel)\ndelite: del /channel_id(or link)\ntags: +asd(add asd tag); -asd(remove sad tag)\nchats - for list chats\ntags - list tags')

@tg_bot.message_handler(commands=['update'])
def helper(msg):
	global acc_info
	if msg.chat.id not in sender.chatIds:
		tg_bot.send_message(msg.chat.id, "Hello, it't bot not for you!")
		return
	acc_info = utils.update_acc_info("Start update account information", msg.chat.id, sender, pars)


@tg_bot.message_handler()
def msg_handel(msg):
	if msg.chat.id not in sender.chatIds:
		tg_bot.send_message(msg.chat.id, "Hello, it't bot not for you!")
		return
	message = msg.json['text']
	if len(message.split(' ')) < 2:
		if message[0] == '+':
			_tag = message[1:]
			if ('#' in _tag):
				if _tag not in pars.users:
					pars.users.append(_tag)
					pars.save_users()
					sender.send_to(f"Username {_tag} added", msg.chat.id)
				else:
					sender.send_to(f'Username "{_tag}" is exists', msg.chat.id)
				return True
			if _tag not in pars.tags:
				pars.tags.append(_tag)
				pars.save_tags()
				sender.send_to(f'Tag "{_tag}" added', msg.chat.id)
			else:
				sender.send_to(f'Tag "{_tag}" is exists', msg.chat.id)
			return True

		if message[0] == '-':
			_tag = message[1:]
			if ('#' in _tag):
				if _tag in pars.users:
					pars.users.remove(_tag)
					pars.save_users()
					sender.send_to(f"Username {_tag} delited", msg.chat.id)
				else:
					sender.send_to(f'Username "{_tag}" not exists', msg.chat.id)
				return True
			if _tag in pars.tags:
				for t in range(len(pars.tags)):
					pars.tags.remove(_tag)
					pars.save_tags()
					sender.send_to(f'Tag "{_tag}" delited', msg.chat.id)
				else:
					sender.send_to(f'Tag "{_tag}" not exists', msg.chat.id)
			return True

		if message.lower() == 'tags':
			tags_list = '\n'.join(pars.tags)
			sender.send_to(f"Tags list\n{tags_list}", msg.chat.id)
			return True

		if message.lower() == 'chats':
			msg_channel_id_str = '\n'.join([f"{d['message_from']} / {d['channel_id']}" for d in pars.data])
			sender.send_to(f"Chat list\n{msg_channel_id_str}", msg.chat.id)
			return True

		if message.lower() == 'users':
			msg_channel_id_str = '\n'.join(pars.users)
			sender.send_to(f"Username list\n{msg_channel_id_str}", msg.chat.id)
			return True

		if message.lower() == 'add':
			markup = types.InlineKeyboardMarkup()
			markup.row_width = 1
			q = [[i['id'], i['name']] for i in acc_info['gls']]
			for i in q:
				markup.add(types.InlineKeyboardButton(i[1], callback_data=f"guild_{i[0]}"))
			markup.add(types.InlineKeyboardButton('Close', callback_data='close'))
			sender.send_to("Choose guild", msg.chat.id, markup)
			return True

		disChatID = message.split('/')[-1:][0]
		if (disChatID not in [d['channel_id'] for d in pars.data]):
			print(f"Try add {disChatID}")
			res = parser.getDisMessage(pars.bot, disChatID)
			if not res:
				sender.send_to(f"Can't get messages from channel", msg.chat.id)
				return False
			res = res.json()
			markup = types.InlineKeyboardMarkup()
			markup.row_width = 2
			markup.add(types.InlineKeyboardButton('Tags', callback_data=f'filter_tags_{disChatID}'), types.InlineKeyboardButton('Roles', callback_data=f'filter_role_{disChatID}'), types.InlineKeyboardButton('From user', callback_data=f'filter_user_{disChatID}'))
			sender.send_to(f"Choose filter", msg.chat.id, markup)
			# res[0]['message_from'] =
			# res[0]['informatin'] =
			# res[0]['filter_type'] =
			res[0]['roles'] = []
			pars.data.append(res[0])
			pars.save_data()
		else:
			sender.send_to(f"Channel {disChatID} in exists\n{next(d for d in pars.data if d['channel_id'] == disChatID)['message_from']}", msg.chat.id)
			return False

		return True
	if len(message.split(' ')) == 2:
		_data = message.split(' ')
		if _data[0] == 'del':
			if _data[1] in [d['channel_id'] for d in pars.data]:
				item = next(d for d in pars.data if d['channel_id'] == _data[1])
				sender.send_to(f"Channel {item['message_from']} delited", msg.chat.id)
				pars.data.remove(item)
				pars.save_data()
			else:
				sender.send_to(f"Channel {_data[1]} not defined", msg.chat.id)

@tg_bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
	global acc_info

	_data = call.data.split('_')

	if _data[0] in ('close', 'guild'):
		tg_bot.edit_message_text(chat_id=call.message.chat.id, text=call.message.json['text'], message_id=call.message.id)
		pars.save_data()

	if _data[0] == 'guild':
		gl = _data[1]
		roles = utils.get_roles(pars.bot, gl)
		if (len(roles) != 0):
			markup = types.InlineKeyboardMarkup()
			markup.row_width = 1
			for i in roles:
				markup.add(types.InlineKeyboardButton(i[1], callback_data=f"roles_{i[0]}_{gl}"))
			markup.add(types.InlineKeyboardButton('Close', callback_data=f"close"))
			tg_bot.send_message(call.message.chat.id, 'Choose roles', reply_markup=markup)
		else:
			tg_bot.send_message(call.message.chat.id, "No roles in guild(or try again)")

	if _data[0] == 'roles':
		chnls = None
		i = 0
		# for i in range(len(acc_info['gls'])):
		while ((i < len(acc_info['gls'])) and (chnls == None)):
			if _data[2] == acc_info['gls'][i]['id']:
				chnls = acc_info['chs'][i]
			i += 1
		# print(chnls)
		chnls = [i['id'] for i in chnls]
		for i, it in enumerate(pars.data):
			if (it['channel_id'] in chnls):
				if (pars.data[i]['filter_type'] == 'role'):
					pars.data[i]['roles'].append(call.data.split('_')[1])
					print(f"added role {_data[1]}")
		markup = types.InlineKeyboardMarkup()
		markup.row_width = 1
		for i in call.message.json['reply_markup']['inline_keyboard']:
			if (i[0]['callback_data'] != call.data):
				markup.add(types.InlineKeyboardButton(i[0]['text'], callback_data=f"{i[0]['callback_data']}"))
		tg_bot.edit_message_text(chat_id=call.message.chat.id, text=call.message.json['text'], message_id=call.message.id, reply_markup=markup)

	if (_data[0] == 'filter'):
		index = None
		ch = 0
		# for ch in range(len(acc_info['chs'])):
		while ((ch < len(acc_info['chs'])) and (index == None)):
			if _data[2] in [ch_id['id'] for ch_id in acc_info['chs'][ch]]:
				index = next(d for d in range(len(pars.data)) if pars.data[d]['channel_id'] == _data[2])
				channel_name = next(c for c in acc_info["chs"][ch] if c['id'] == _data[2])['name']
				pars.data[index]['informatin'] = f'https://discord.com/channels/{acc_info["gls"][ch]["id"]}/{_data[2]}/'
				pars.data[index]['message_from'] = f'{acc_info["gls"][ch]["name"]} / {channel_name}'
				print(index)
			ch += 1
		if index == None:
			acc_info = utils.update_acc_info("Server with chat not defined, updating account information...", call.message.chat.id, sender, pars)
			sender.send_to(f"Try again add channel")
			return False
		pars.data[index]['filter_type'] = _data[1]
		tg_bot.edit_message_text(chat_id=call.message.chat.id, text=f'Chat {_data[2]} added', message_id=call.message.id)
		print("Filter added", index)
		pars.save_data()

def main():
	while 1:
		_data = pars.parse_mess()
		pars.data = _data['full_mess']
		for message in _data['send_mess']:
			# print(message)
			sender.send_all(f"{message['message_from']}\n\n{message['informatin'] + message['id']}\n\n{message['content']}")
			time.sleep(0.5)
		pars.save_data()
		time.sleep(15)

if __name__ == "__main__":
	print("Bot start work")
	print("DEV tg @Kokouh")
	threading.Thread(target=main, args=()).start()
	tg_bot.infinity_polling()
# sender.send_all('Hellow')
