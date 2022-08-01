import json
import time

def update_acc_info(message, chatId, sender, pars):
	sender.send_to(message, chatId)
	print('\nStart update acc_info')
	gls = pars.bot.getGuilds().json()
	chs = []
	for i in range(len(gls)):
		chs.append(pars.bot.getGuildChannels(gls[i]['id']).json())
		time.sleep(2)
		print(f"\r{round((i+1)/len(gls) * 100, 2)} %")

	acc_info = {"gls":gls, 'chs':chs}
	with open('data/acc_info.json', 'wb') as f:
		f.write(json.dumps(acc_info).encode('utf8'))
	
	sender.send_to("Account information updated", chatId)
	return (acc_info)

def get_roles(cl, guild):
	r = cl.s.get(f'https://discord.com/api/v9/guilds/{guild}/roles')
	if r.status_code == 200:
		return ([[i['id'], i['name']] for i in r.json()])
	return ([])