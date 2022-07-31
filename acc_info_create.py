import discum
import json
import time

cl = discum.Client(token='OTY5ODA2NTc1Mjk0MzQ5MzUy.YmyyiA.qVi97u1y5dkDjPVQFKtff151IDc', log=False)

print('\nStart update acc_info')
gls = cl.getGuilds().json()
chs = []
for i in range(len(gls)):
	chs.append(cl.getGuildChannels(gls[i]['id']).json())
	time.sleep(2)
	print(f"\r{round((i+1)/len(gls) * 100, 2)} %")

with open('data/acc_info.json', 'wb') as f:
	f.write(json.dumps({"gls":gls, 'chs':chs}).encode('utf8'))