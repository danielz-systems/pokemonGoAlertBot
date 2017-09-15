#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from time import sleep
import time
from datetime import datetime, tzinfo, timedelta
import requests
import os
import telepot
import json
import ConfigParser

config = ConfigParser.ConfigParser()
config.read("telegram.config")

token1 = config.get('Telegram', 'token1')
token2 = config.get('Telegram', 'token2')


pokeChat_ids = []
raidChat_ids = []

fobj = open("pokeChatIds", "r")
for line in fobj: 
	line = line.strip() 
	data = line.split(";")
	user = {}
	user["id"] = data[0]
	user["pokemon"] = []
#	user["sendLocation"] = json.loads(data[2])
	user["sendLocation"] = data[2]
	pokelist = data[1].replace('[', '')
	pokelist = pokelist.replace(']', '')
	pokelist = pokelist.replace("'", "")
	for id in pokelist.split(","):
		if id:
			user["pokemon"].append(int(id))
	pokeChat_ids.append(user)
fobj.close()

importantPokemons = []
for user in pokeChat_ids:
	for pokeId in user["pokemon"]:
		if not pokeId in importantPokemons:
			importantPokemons.append(int(pokeId))

fobj = open("raidChatIds", "r")
for line in fobj:
	line = line.strip()
	data = line.split(";")
	user = {}
	user["id"] = data[0]
	user["sendLocation"] = data[1]
	raidChat_ids.append(user)
fobj.close()

def pokeHandle(msg):
	global importantPokemons
	chat_id = msg['chat']['id']
	try:
		command = msg['text']
	except:
		command = ""


	print chat_id
	print 'Got command: %s' % command

	if command == '/start':
		for user in pokeChat_ids:
			if chat_id == int(user["id"]):
				return
		user = {}
		user["id"] = chat_id
		user["pokemon"] = []
		user["sendLocation"] = True
		pokeChat_ids.append(user)
		fobj = open("pokeChatIds", "w")
		for user in pokeChat_ids:
			fobj.write(str(user["id"]) + ";" + str(user["pokemon"]) + ";" + str(user["sendLocation"]) + '\n')
		fobj.close()
		msg = "Gude, ab sofort verpasst du keine wichtigen Spawns in der Umgebung ca. 20 km rund um Obernburg mehr!"
		pokeBot.sendMessage(chat_id,msg)
	elif command == '/stop':
		for user in pokeChat_ids:
			if chat_id == int(user["id"]):
				pokeChat_ids.remove(user)
				fobj = open("pokeChatIds", "w")
				for user in pokeChat_ids:
					fobj.write(str(user["id"]) + ";" + str(user["pokemon"]) + ";" + str(user["sendLocation"]) + '\n')
				fobj.close()
				msg = "Schade, wir haben deine Abmeldung registriert"
				pokeBot.sendMessage(chat_id, msg)
				return
	elif command == "/pokelist":
		for user in pokeChat_ids:
			if int(user["id"]) == chat_id:
				msg = "Du erhaeltst Benachrichtigungen fuer folgende Pokemon: \n"
				for id in user["pokemon"]:
					msg += pokeNames[id] + "\n"
				pokeBot.sendMessage(chat_id, msg)
				msg += "Schicke einfach einen Pokemon Namen um es hinzuzufuegen oder zu entfernen!"
				return
	
	elif command == "/sendlocation":
		for user in pokeChat_ids:
			if int(user["id"]) == chat_id:
				if user["sendLocation"] == True or user["sendLocation"] == "True":
					user["sendLocation"] = False
				else:
					user["sendLocation"] = True
				msg = "Send Location ist jetzt: " + str(user["sendLocation"])
				pokeBot.sendMessage(chat_id, msg)
				fobj = open("pokeChatIds", "w")
				for user in pokeChat_ids:
					fobj.write(str(user["id"]) + ";" + str(user["pokemon"]) + ";" + str(user["sendLocation"]) + '\n')
				fobj.close()
				return

	elif command.replace('/', '').lower() in pokemonDict:
		for user in pokeChat_ids:
			if int(user["id"]) == chat_id:
				command = command.replace('/', '').lower()
				print "pokemonDict[command]",pokemonDict[command]
				
				if pokemonDict[command] in user["pokemon"]:
					user["pokemon"].remove(pokemonDict[command])
					msg = command + " wurde aus deiner Benachrichtigungsliste entfernt!"
					pokeBot.sendMessage(chat_id, msg)
				else:
					user["pokemon"].append(pokemonDict[command])
					msg = command + " wurde zu deiner Benachrichtigungsliste hinzugefuegt!"
					pokeBot.sendMessage(chat_id, msg)
				fobj = open("pokeChatIds", "w")
				for user in pokeChat_ids:
					fobj.write(str(user["id"]) + ";" + str(user["pokemon"]) + ";" + str(user["sendLocation"]) + '\n')
				fobj.close()
				importantPokemons = []
				for user in pokeChat_ids:
					for pokeId in user["pokemon"]:
						if not pokeId in importantPokemons:
							importantPokemons.append(int(pokeId))
				return
	else:
		msg = "Der Befehl " + command + " ist leider nicht bekannt."
		pokeBot.sendMessage(chat_id, msg)



def raidHandle(msg):
	chat_id = msg['chat']['id']
	try:
		command = msg['text']
	except:
		command = ""

	print chat_id
	print 'Got command: %s' % command
	if command == '/start':
		for user in raidChat_ids:
			if chat_id == int(user["id"]):
				return
		user = {}
		user["id"] = chat_id
		user["sendLocation"] = True
		raidChat_ids.append(user)
		fobj = open("raidChatIds", "w")
		for user in raidChat_ids:
			fobj.write(str(user["id"]) + ";" + str(user["sendLocation"]) + '\n')
		fobj.close()
		msg = "Gude, ab sofort verpasst du keine Level 4 und 5 Raids in der Umgebung ca. 20 km rund um Obernburg mehr!"
		raidBot.sendMessage(chat_id,msg)
	elif command == '/stop':
		for user in raidChat_ids:
			if chat_id == int(user["id"]):
				raidChat_ids.remove(user)
				fobj = open("raidChatIds", "w")
				for user in raidChat_ids:
					fobj.write(str(user["id"]) + ";" + str(user["sendLocation"]) + '\n')
				fobj.close()
				msg = "Schade, wir haben deine Abmeldung registriert"
				raidBot.sendMessage(chat_id, msg)
				return	
	elif command == "/sendlocation":
		for user in raidChat_ids:
			if int(user["id"]) == chat_id:
				if user["sendLocation"] == True or user["sendLocation"] == "True":
					user["sendLocation"] = False
				else:
					user["sendLocation"] = True
				msg = "Send Location ist jetzt: " + str(user["sendLocation"])
				raidBot.sendMessage(chat_id, msg)
				fobj = open("raidChatids", "w")
				for user in raidChat_ids:
					fobj.write(str(user["id"]) + ";" + str(user["sendLocation"]) + '\n')
				fobj.close()
				return

def sendPokeMessage(pokemonId,msg,lat,long):
	for user in pokeChat_ids:
		if pokemonId in user["pokemon"]:
			try:
				pokeBot.sendMessage(user["id"], msg)
				sleep(0.1)
				if user["sendLocation"] == True or user["sendLocation"] == "True":
					pokeBot.sendLocation(user["id"],lat,long,True)
					sleep(0.1)
			except Exception, e:
				print "Error:" + str(e[0]) + " chat id: " + str(user["id"])
				if str(e[0]) == "Forbidden: bot was blocked by the user":
					pokeChat_ids.remove(user)
					fobj = open("pokeChatIds", "w")
					for user in pokeChat_ids:
						fobj.write(str(user["id"]) + ";" + str(user["pokemon"]) + ";" + user["sendLocation"] + '\n')
					fobj.close()


def sendRaidMessage(msg,lat,long):
	for user in raidChat_ids:
		try:
			raidBot.sendMessage(user["id"], msg)
			sleep(0.1)
			if user["sendLocation"] == True or user["sendLocation"] == "True":
				raidBot.sendLocation(user["id"],lat,long,True)
				sleep(0.1)
		except Exception, e:
			print "Error:" + str(e[0]) + " chat id: " + str(user["id"])
			if str(e[0]) == "Forbidden: bot was blocked by the user":
				raidChat_ids.remove(user)
				fobj = open("raidChatIds", "w")
				for user in raidChat_ids:
					fobj.write(str(user["id"])  + ";" + str(user["sendLocation"]) + '\n')
				fobj.close()

def getAddress(lat,long):
	url = "http://nominatim.openstreetmap.org/reverse?format=json&lat=" + str(lat) + "&lon=" + str(long) + "&zoom=18&addressdetails=1"
	try:
		r = requests.get(url)
		data = r.json()
		address = data["address"]
	except:
		data = ""
		return data

	city = ""
	if "suburb" in address:
		city = address["suburb"]
		if "town" in address:
			city += " - " + address["town"]
	elif "city_district" in address:
		city = address["city_district"]
	elif "village" in address:
		city = address["village"]
	elif "town" in address:
		city = address["town"]
	elif "city" in address:
		city = address["city"]

	street = ""
	if "road" in address:
		street = address["road"]
		if ("house_number" in address):
			street += " " + str(address["house_number"])
			city += " - " + street 

	return city


pokeBot = telepot.Bot(token1)
pokeBot.message_loop(pokeHandle)

raidBot = telepot.Bot(token2)
raidBot.message_loop(raidHandle)

running = True

url = "https://mapdata2.gomap.eu/mnew.php?mid="
#urlCoords = "w=8.867998151123049&e=9.400983404541017&n=50.11150611116903&s=49.60758358582943"
urlCoords = "w=8.979786000000000&e=9.241398000000000&n=50.0071140000000&s=49.70000000000000"


#importantPokemons = [83,115,128,130,131,143,149,154,157,160,179,180,181,201,214,222,237,241,242,246,247,248,114,113,137,144,146,145,150,151,233,250,249,251]
maxeid = 0
maxgid = 0
firstRun = True

pokeNames = ["", "Bisasam", "Bisaknosp", "Bisaflor", "Glumanda", "Glutexo", "Glurak", "Schiggy", "Schillok", "Turtok", "Raupy", "Safcon", "Smettbo", "Hornliu", "Kokuna", "Bibor", "Taubsi", "Tauboga", "Tauboss", "Rattfratz", "Rattikarl", "Habitak", "Ibitak", "Rettan", "Arbok", "Pikachu", "Raichu", "Sandan", "Sandamer", "NidoranW", "Nidorina", "Nidoqueen", "NidoranM", "Nidorino", "Nidoking", "Piepi", "Pixi", "Vulpix", "Vulnona", "Pummeluff", "Knuddeluff", "Zubat", "Golbat", "Myrapla", "Duflor", "Giflor", "Paras", "Parasek", "Bluzuk", "Omot", "Digda", "Digdri", "Mauzi", "Snobilikat", "Enton", "Entoron", "Menki", "Rasaff", "Fukano", "Arkani", "Quapsel", "Quaputzi", "Quappo", "Abra", "Kadabra", "Simsala", "Machollo", "Maschock", "Machomei", "Knofensa", "Ultrigaria", "Sarzenia", "Tentacha", "Tentoxa", "Kleinstein", "Georok", "Geowaz", "Ponita", "Gallopa", "Flegmon", "Lahmus", "Magnetilo", "Magneton", "Porenta", "Dodu", "Dodri", "Jurob", "Jugong", "Sleima", "Sleimok", "Muschas", "Austos", "Nebulak", "Alpollo", "Gengar", "Onix", "Traumato", "Hypno", "Krabby", "Kingler", "Voltobal", "Lektrobal", "Owei", "Kokowei", "Tragosso", "Knogga", "Kicklee", "Nockchan", "Schlurp", "Smogon", "Smogmog", "Rihorn", "Rizeros", "Chaneira", "Tangela", "Kangama", "Seeper", "Seemon", "Goldini", "Golking", "Sterndu", "Starmie", "Pantimos", "Sichlor", "Rossana", "Elektek", "Magmar", "Pinsir", "Tauros", "Karpador", "Garados", "Lapras", "Ditto", "Evoli", "Aquana", "Blitza", "Flamara", "Porygon", "Amonitas", "Amoroso", "Kabuto", "Kabutops", "Aerodactyl", "Relaxo", "Arktos", "Zapdos", "Lavados", "Dratini", "Dragonir", "Dragoran", "Mewtu", "Mew", "Endivie", "Lorblatt", "Meganie", "Feurigel", "Igelavar", "Tornupto", "Karnimani", "Tyracroc", "Impergator", "Wiesor", "Wiesenior", "Hoothoot", "Noctuh", "Ledyba", "Ledian", "Webarak", "Ariados", "Iksbat", "Lampi", "Lanturn", "Pichu", "Pii", "Fluffeluff", "Togepi", "Togetic", "Natu", "Xatu", "Voltilamm", "Waaty", "Ampharos", "Blubella", "Marill", "Azumarill", "Mogelbaum", "Quaxo", "Hoppspross", "Hubelupf", "Papungha", "Griffel", "Sonnkern", "Sonnflora", "Yanma", "Felino", "Morlord", "Psiana", "Nachtara", "Kramurx", "Laschoking", "Traunfugil", "Icognito", "Woingenau", "Girafarig", "Tannza", "Forstellka", "Dummisel", "Skorgla", "Stahlos", "Snubbull", "Granbull", "Baldorfish", "Scherox", "Pottrott", "Skaraborn", "Sniebel", "Teddiursa", "Ursaring", "Schneckmag", "Magcargo", "Quiekel", "Keifel", "Corasonn", "Remoraid", "Octillery", "Botogel", "Mantax", "Panzaeron", "Hunduster", "Hundemon", "Seedraking", "Phanpy", "Donphan", "Porygon2", "Damhirplex", "Farbeagle", "Rabauz", "Kapoera", "Kussilla", "Elekid", "Magby", "Miltank", "Heiteira", "Raikou", "Entei", "Suicune", "Larvitar", "Pupitar", "Despotar", "Lugia", "Ho-Oh", "Celebi", "Geckarbor", "Reptain", "Gewaldro", "Flemmli", "Jungglut", "Lohgock", "Hydropi", "Moorabbel", "Sumpex", "Fiffyen", "Magnayen", "Zigzachs", "Geradaks", "Waumpel", "Schaloko", "Papinella", "Panekon", "Pudox", "Loturzel", "Lombrero", "Kappalores", "Samurzel", "Blanas", "Tengulist", "Schwalbini", "Schwalboss", "Wingull", "Pelipper", "Trasla", "Kirlia", "Guardevoir", "Gehweiher", "Maskeregen", "Knilz", "Kapilz", "Bummelz", "Muntier", "Letarking", "Nincada", "Ninjask", "Ninjatom", "Flurmel", "Krakeelo", "Krawumms", "Makuhita", "Hariyama", "Azurill", "Nasgnet", "Eneco", "Enekoro", "Zobiris", "Flunkifer", "Stollunior", "Stollrak", "Stolloss", "Meditie", "Meditalis", "Frizelbliz", "Voltenso", "Plusle", "Minun", "Volbeat", "Illumise", "Roselia", "Schluppuck", "Schlukwech", "Kanivanha", "Tohaido", "Wailmer", "Wailord", "Camaub", "Camerupt", "Qurtel", "Spoink", "Groink", "Pandir", "Knacklion", "Vibrava", "Libelldra", "Tuska", "Noktuska", "Wablu", "Altaria", "Sengo", "Vipitis", "Lunastein", "Sonnfel", "Schmerbe", "Welsar", "Krebscorps", "Krebutack", "Puppance", "Lepumentas", "Liliep", "Wielie", "Anorith", "Armaldo", "Barschwa", "Milotic", "Formeo", "Kecleon", "Shuppet", "Banette", "Zwirrlicht", "Zwirrklop", "Tropius", "Palimpalim", "Absol", "Isso", "Schneppke", "Firnontor", "Seemops", "Seejong", "Walraisa", "Perlu", "Aalabyss", "Saganabyss", "Relicanth", "Liebiskus", "Kindwurm", "Draschel", "Brutalanda", "Tanhel", "Metang", "Metagross", "Regirock", "Regice", "Registeel", "Latias", "Latios", "Kyogre", "Groudon", "Rayquaza", "Jirachi", "Deoxys", "Chelast", "Chelcarain", "Chelterrar", "Panflam", "Panpyro", "Panferno", "Plinfa", "Pliprin", "Impoleon", "Staralili", "Staravia", "Staraptor", "Bidiza", "Bidifas", "Zirpurze", "Zirpeise", "Sheinux", "Luxio", "Luxtra", "Knospi", "Roserade", "Koknodon", "Rameidon", "Schilterus", "Bollterus", "Burmy", "Burmadame", "Moterpel", "Wadribie", "Honweisel", "Pachirisu", "Bamelin", "Bojelin", "Kikugi", "Kinoso", "Schalellos", "Gastrodon", "Ambidiffel", "Driftlon", "Drifzepeli", "Haspiror", "Schlapor", "Traunmagil", "Kramshef", "Charmian", "Shnurgarst", "Klingplim", "Skunkapuh", "Skuntank", "Bronzel", "Bronzong", "Mobai", "Pantimimi", "Wonneira", "Plaudagei", "Kryppuk", "Kaumalat", "Knarksel", "Knakrack", "Mampfaxo", "Riolu", "Lucario", "Hippopotas", "Hippoterus", "Pionskora", "Piondragi", "Glibunkel", "Toxiquak", "Venuflibis", "Finneon", "Lumineon", "Mantirps", "Shnebedeck", "Rexblisar", "Snibunna", "Magnezone", "Schlurplek", "Rihornior", "Tangoloss", "Elevoltek", "Magbrant", "Togekiss", "Yanmega", "Folipurba", "Glaziola", "Skorgro", "Mamutel", "Porygon-Z", "Galagladi", "Voluminas", "Zwirrfinst", "Frosdedje", "Rotom", "Selfe", "Vesprit", "Tobutz", "Dialga", "Palkia", "Heatran", "Regigigas", "Giratina", "Cresselia", "Phione", "Manaphy", "Darkrai", "Shaymin", "Arceus", "Victini", "Serpifeu", "Efoserp", "Serpiroyal", "Floink", "Ferkokel", "Flambirex", "Ottaro", "Zwottronin", "Admurai", "Nagelotz", "Kukmarda", "Yorkleff", "Terribark", "Bissbark", "Felilou", "Kleoparda", "Vegimak", "Vegichita", "Grillmak", "Grillchita", "Sodamak", "Sodachita", "Somniam", "Somnivora", "Dusselgurr", "Navitaub", "Fasasnob", "Elezeba", "Zebritz", "Kiesling", "Sedimantur", "Brockoloss", "Fleknoil", "Fletiamo", "Rotomurf", "Stalobor", "Ohrdoch", "Praktibalk", "Strepoli", "Meistagrif", "Schallquap", "Mebrana", "Branawarz", "Jiutesto", "Karadonis", "Strawickl", "Folikon", "Matrifol", "Toxiped", "Rollum", "Cerapendra", "Waumboll", "Elfun", "Lilminip", "Dressella", "Barschuft", "Ganovil", "Rokkaiman", "Rabigator", "Flampion", "Flampivian", "Maracamba", "Lithomith", "Castellith", "Zurrokex", "Irokex", "Symvolara", "Makabaja", "Echnatoll", "Galapaflos", "Karippas", "Flapteryx", "Aeropteryx", "Unrat&uuml;tox", "Deponitox", "Zorua", "Zoroark", "Picochilla", "Chillabell", "Mollimorba", "Hypnomorba", "Morbitesse", "Monozyto", "Mitodos", "Zytomega", "Piccolente", "Swaroness", "Gelatini", "Gelatroppo", "Gelatwino", "Sesokitz", "Kronjuwild", "Emolga", "Laukaps", "Cavalanzas", "Tarnpignon", "Hutsassa", "Quabbel", "Apoquallyp", "Mamolida", "Wattzapf", "Voltula", "Kastadur", "Tentantel", "Klikk", "Kliklak", "Klikdiklak", "Zapplardin", "Zapplalek", "Zapplarang", "Pygraulon", "Megalon", "Lichtel", "Laternecto", "Skelabra", "Milza", "Sharfax", "Maxax", "Petznief", "Siberio", "Frigometri", "Schnuthelm", "Hydragil", "Flunschlik", "Lin-Fu", "Wie-Shu", "Shardrago", "Golbit", "Golgantes", "Gladiantri", "Caesurio", "Bisofank", "Geronimatz", "Washakwil", "Skallyk", "Grypheldis", "Furnifrass", "Fermicula", "Kapuno", "Duodino", "Trikephalo", "Ignivor", "Ramoth", "Kobalium", "Terrakium", "Viridium", "Boreos", "Voltolos", "Reshiram", "Zekrom", "Demeteros", "Kyurem", "Keldeo", "Meloetta", "Genesect", "Igamaro", "Igastarnish", "Brigaron", "Fynx", "Rutena", "Fennexis", "Froxy", "Amphizel", "Quajutsu", "Scoppel", "Grebbit", "Dartiri", "Dartignis", "Fiaro", "Purmel", "Puponcho", "Vivillon", "Leufeo", "Pyroleo", "Flab&eacute;b&eacute;", "FLOETTE", "Florges", "M&auml;hikel", "Chevrumm", "Pam-Pam", "Pandagro", "Coiffwaff", "Psiau", "Psiaugon", "Gramokles", "Duokles", "Durengard", "Parfi", "Parfinesse", "Flauschling", "Sabbaione", "Iscalar", "Calamanero", "Bithora", "Thanathora", "Algitt", "Tandrak", "Scampisto", "Wummer", "Eguana", "Elezard", "Balgoras", "Monargoras", "Amarino", "Amagarga", "Feelinara", "Resladero", "DEDENNE", "Rocara", "Viscora", "Viscargot", "Viscogon", "Clavion", "Paragoni", "Trombork", "Irrbis", "Pumpdjinn", "Arktip", "Arktilas", "eF-eM", "UHaFnir", "Xerneas", "Yveltal", "Zygarde", "Diancie", "Hoopa", "Volcanion"]
pokemonDict = {}
id = 0
for pokemon in pokeNames:
	pokemonDict[pokemon.lower()] = id
	id += 1
#print pokemonDict


print 'Poke Map Bot started'


while running:
	try:
		r = requests.get(url + str(maxeid) + "&" + urlCoords + "&gid=" + str(maxgid))
		data = r.json()
		pokemons = data["pokemons"]
		gyms = data["gyms"]
		if firstRun:
			print "pokemons", pokemons
			sleep(2)
#			print "gyms", gyms
		for pokemon in pokemons:
			if pokemon["eid"] > maxeid:
				maxeid = pokemon["eid"]
#			print "new poke", pokemon["pokemon_id"], pokeNames[pokemon["pokemon_id"]]
			if pokemon["pokemon_id"] in importantPokemons and not firstRun:

				address = getAddress(pokemon["latitude"],pokemon["longitude"])
				if address != "":
					msg = "Pokemon spawned: " + pokeNames[pokemon["pokemon_id"]] + " / " + str(pokemon["pokemon_id"]) + " in " + address + " bis " + str(datetime.fromtimestamp(pokemon["disappear_time"]).time())
				else:
					msg = "Pokemon spawned: " + pokeNames[pokemon["pokemon_id"]] + " / " + str(pokemon["pokemon_id"]) + " bis " + str(datetime.fromtimestamp(pokemon["disappear_time"]).time())
				print msg
				if not firstRun:
					sendPokeMessage(pokemon["pokemon_id"],msg,pokemon["latitude"],pokemon["longitude"])


		ts = int(round(time.time()))
		maxgid = ts
		for gym in gyms:
			if "rs" in gym:
				if gym["lvl"] > 3:
					msg = ""
					address = getAddress(gym["latitude"],gym["longitude"])
					if(ts > gym["rs"] and ts < gym["rb"]):
						msg = "Level " + str(gym["lvl"]) + " Raid in " + address + " um " + str(datetime.fromtimestamp(gym["rb"]).time()) + " Uhr."
					elif (ts > gym["rb"] and ts < gym["re"]):
						msg = "Level " + str(gym["lvl"]) + " Raid in " + address + " bis " + str(datetime.fromtimestamp(gym["re"]).time()) + " Uhr."
					if (gym["rpid"]>0):
						msg += " Mit Pokemon " + pokeNames[gym["rpid"]] + " mit " + str(gym["rcp"]) + " CP."                
					print msg
					if len(msg) > 0:
						if not firstRun:
							sendRaidMessage(msg,gym["latitude"],gym["longitude"])

	except Exception, e:
		print "Error:" + str(e[0])

	firstRun = False
	sleep(20)
