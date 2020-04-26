import hashlib

a = {"domain": "www.immonet.de", "date": "2020-04-26", "expose": "40118524", "coldrent": "381,21", "roomnumber": "2", "surface": "52,22", "sidecosts": "65,00"}
b = {"domain": "www.immobilienscout24.de", "date": "2020-04-26", "expose": "117117705", "coldrent": "381,21", "roomnumber": "2", "surface": "52,22", "sidecosts": "65,00"}

ah = hashlib.md5((str(a['coldrent']) + str(a['surface']) + str(a['roomnumber']) + str(a['sidecosts'])).encode('utf-8')).digest()
bh = hashlib.md5((str(b['coldrent']) + str(b['surface']) + str(b['roomnumber']) + str(b['sidecosts'])).encode('utf-8')).digest()
c = set()

c.add(ah)
print(ah)
print(bh)
print(bh in c)