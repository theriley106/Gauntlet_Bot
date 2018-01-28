import requests
import bs4
import threading
import re
import traceback
import json
import RandomHeaders
import time
from selenium import webdriver

def grabSite(url, retry=False):
	failCount = 0
	headers = {'User-Agent': '{}'.format(RandomHeaders.LoadHeader())}
	try:
		res = requests.get(url, headers=headers, timeout=5)
	except:
		res = None
	while res.status_code != 200 and failCount < 5 and retry == True:
		try:
			print("Network Failed: {}".format(url))
			# this will reattempt to grab the page 5 times if you specify retry as true
			res = requests.get(url, headers=headers)
		except:
			res = None
			failCount = failCount + 1
	if failCount > 3:
		res = None
	return res

def chunks(l, n):
	for i in xrange(0, len(l), n):
		yield l[i:i + n]

def returnVar(page, var):
	return re.findall("'>{}<span>(\d+)</span></li>".format(var), str(page))[0]



def genClass(playNum):
	return '.instance_card_{}'.format(playNum)

def loadDatabase(databaseName='primaryDB.json'):
	with open(databaseName) as json_data:
		return json.load(json_data)


def oldReturnPlayerInfo(playNumList):
	tempInfo = []
	for val in playNumList:
		try:
			print("{}".format(len(fullDB)))
			playNum = val['Number']
			information = {}
			information["playerNum"] = playNum
			res = grabSite("http://www.muthead.com/18/players/{}/tooltip".format(playNum))
			if res != None:
				page = bs4.BeautifulSoup(res.text, 'lxml')
				Foot, Inch = re.findall("\d+", str(re.findall("'>{}<span>(.+)</span></li>".format("HT"), str(page))).partition('"<')[0])
				information["instanceID"] = re.findall("instance_card_(\d+)", str(page))[0]
				information["Overall"] = re.findall("(\d+)", str(page).partition("overall")[2].partition("span")[0])[0]
				information["Position"] = re.findall("(\w+)", str(page).partition("position")[2].partition("span")[0])[0]
				information["First_Name"] = re.findall("(\w+)", str(page).partition("first-and-last-name")[2].partition("span")[0])[0]
				information["Last_Name"] = re.findall("(\w+)", str(page).partition("first-and-last-name")[2].partition("span")[0])[-1]
				information["Full_Name"] = ' '.join(re.findall("(\w+)", str(page).partition("first-and-last-name")[2].partition("span")[0]))
				information["HT"] = {"Feet": Foot, "Inch": Inch}
				for var in re.findall("(\w+)<span>\d", str(page))[1:]:
					information[var] = returnVar(page, var)
				fullDB.append(information)
		except Exception as exp:
			if 'keyboardinterrupt' in str(exp).lower():
				sys.exit(0)
			else:
				traceback.print_exc()

def grabAllStats(playerID):
	information = {}
	res = grabSite("http://www.muthead.com/18/players/{}/full-ratings".format(playerID))
	page = bs4.BeautifulSoup(res.text, 'lxml')
	selection = page.select(".player-details-left .player-details-stats span")
	for i in range(0, len(selection), 2):
		try:
			information[str(selection[i:i+2][-1].strip())] = int(selection[i:i+2][0].strip())
		except:
			print("Error")
	return information


def grabMoreInfoAboutPlayers():
	fullDB = []
	lock = threading.Lock()
	data = loadDatabase('database.json')
	data = chunks(data, int(len(data)/25))
	#this makes it so you can have 25 threads running simultaniously
	def returnPlayerInfo(playNumList):
		tempInfo = []
		for val in playNumList:
			try:
				print("{}".format(len(fullDB)))
				playNum = val['Number']
				information = {}
				information["playerNum"] = playNum
				res = grabSite("http://www.muthead.com/18/players/{}/full-ratings".format(playNum))
				if res != None:
					page = bs4.BeautifulSoup(res.text, 'lxml')
					selection = page.select(".player-details-left .player-details-stats span")
					for i in range(0, len(selection), 2):
						try:
							keyw = str(selection[i:i+2][-1].getText()).strip()
							valw = int(selection[i:i+2][0].getText().strip())
							information[keyw] = valw
						except Exception as exp:
							traceback.print_exc()
					res = grabSite("http://www.muthead.com/18/players/{}/tooltip".format(playNum))
					if res != None:
						page = bs4.BeautifulSoup(res.text, 'lxml')
						Foot, Inch = re.findall("\d+", str(re.findall("'>{}<span>(.+)</span></li>".format("HT"), str(page))).partition('"<')[0])
						information["instanceID"] = re.findall("instance_card_(\d+)", str(page))[0]
						information["Overall"] = re.findall("(\d+)", str(page).partition("overall")[2].partition("span")[0])[0]
						information["Position"] = re.findall("(\w+)", str(page).partition("position")[2].partition("span")[0])[0]
						information["First_Name"] = re.findall("(\w+)", str(page).partition("first-and-last-name")[2].partition("span")[0])[0]
						information["Last_Name"] = re.findall("(\w+)", str(page).partition("first-and-last-name")[2].partition("span")[0])[-1]
						information["Full_Name"] = ' '.join(re.findall("(\w+)", str(page).partition("first-and-last-name")[2].partition("span")[0]))
						information["HT"] = {"Feet": Foot, "Inch": Inch}
				fullDB.append(information)
			except Exception as exp:
				if 'keyboardinterrupt' in str(exp).lower():
					sys.exit(0)
				else:
					traceback.print_exc()
	threads = [threading.Thread(target=returnPlayerInfo, args=(ar,)) for ar in data]

	for thread in threads:
		thread.start()
	for thread in threads:
		thread.join()
	with open("Database.json", 'w') as fout:
		json.dump(fullDB, fout)

def grabAllPlayersNums(verbose=True, saveAs="database.json"):
	#This grabs every player number from Muthead - it generates that primaryDB.json
	playerDB = []
	for pageNum in range(1,218):
		#range should be page num + 1
		try:
			#Grabs page_1 to page_213
			url = "http://www.muthead.com/18/players?page={}".format(pageNum)
			print url
			res = grabSite(url, retry=True)
			page = bs4.BeautifulSoup(res.text, 'lxml')
			for elem in page.select(".name-program a"):
				playerName = elem.getText().strip()
				playerNumber = re.findall("\d+", str(elem).partition("/players/")[2])[0]
				playerDB.append({"Name": playerName, "Number": playerNumber})
			if verbose == True:
				print(page.title.string)
		except Exception as exp:
			if 'keyboardinterrupt' in str(exp).lower():
				sys.exit(0)
			else:
				traceback.print_exc()
		with open(saveAs, 'w') as fout:
			json.dump(playerDB, fout)

def extractCardNum(cardNumElem):
	re.findall("instance_card_(\d+)", str(cardNumElem))
	instance_card_

class startBot(object):
	"""docstring for startBot"""
	def __init__(self, loginType=None, username=None, password=None, verbose=False, webAddress='http://www.muthead.com/gauntlet'):
		self.Database = loadDatabase("src/Database.json")
		self.verbose = verbose
		self.webAddress = webAddress
		if loginType == None:
			self.autoLogin = False
		else:
			self.autoLogin = True
		self.driver = webdriver.Firefox()
		#This "Starts" the browser that we will automate
		if self.autoLogin == True:
			print("Auto-login is not currently supported")
			self.autoLogin = False
			#self.autoLogin = self.login(loginType, username, password)
			# this attempts to login
		if self.autoLogin == False:
			if loginType != None:
				self.driver.get("https://www.muthead.com/{}-login".format(loginType.lower()))
			else:
				self.driver.get("https://www.muthead.com/login")
			# this goes to the login screen
			raw_input("You'll have to login manually.  Click enter after successful login: ")

		self.driver.set_page_load_timeout(30)
		#self.driver.get()

	def login(self, loginType, username, password):
		self.driver.get("https://www.muthead.com/{}-login".format(loginType.lower()))
		if loginType.lower() == 'twitch':
			time.sleep(10)
			# twitch requires a huge timeout for some reason...
			self.driver.find_element_by_id("username").clear().send_keys(username)
			time.sleep(.5)
			# micro pause between the two inputs
			self.driver.find_element_by_id("password").clear().send_keys(password)
			self.driver.find_element_by_xpath("//button[@type='submit']").click()
			#this is the submit button to login
			time.sleep(5)

		elif login.lower() == 'curse':
			time.sleep(5)
			# curse requires a slightly shorter timeout
			self.driver.find_element_by_id("field-loginFormPassword").clear().send_keys(username)
			time.sleep(.5)
			# micro pause between the two inputs
			self.driver.find_element_by_id("field-loginFormPassword").clear().send_keys(password)
			self.driver.find_element_by_css_selector("button.u-button.u-button-z").click()
			# this is the submit button for curse
			time.sleep(5)
		if self.driver.current_url == 'http://www.muthead.com/':
			return True
		else:
			return False
	def returnPlayerValue(self, instanceID, value):
		for val in self.Database:
			if val["instanceID"] == instanceID:
				try:
					returnVal = val[value]
					return returnVal
				except:
					pass
		return 0

	def getCurrentPlayersOnScreen(self):
		playersOnScreen = []
		htmlElement = self.driver.find_element_by_css_selector(".gauntlet-choices").get_attribute('innerHTML')
		cardsOnScreen = re.findall("\sinstance_card_(\d+)", str(htmlElement))
		variable = self.extractVarFromQuestion(self.returnQuestion())
		if len(cardsOnScreen) == 3:
			for i, idValue in enumerate(cardsOnScreen):
				playersOnScreen.append({"ID": idValue, "Index": i, "Value": self.returnPlayerValue(idValue, variable)})
			return int(sorted(playersOnScreen, key=lambda k: k['Value'], reverse=True)[0]["ID"])

		else:
			return None

	def getPlayableChoices(self):
		return self.driver.find_element_by_css_selector(".gauntlet-choices .playable").get_attribute('innerHTML')

	def startGame(self):
		self.driver.get("http://www.muthead.com/gauntlet")

	def returnQuestion(self):
		questionRaw = self.driver.find_element_by_css_selector(".question").get_attribute('innerHTML')
		return str(re.sub("(<!--.*?-->)", "", questionRaw, flags=re.MULTILINE))

	def extractVarFromQuestion(self, question):
		return question.partition(")?")[0].partition(" (")[2]

	def solveQuestionOnScreen(self):
		self.driver.find_element_by_css_selector(genClass(self.getCurrentPlayersOnScreen())).click()

	def clickContinueButton(self):
		self.driver.find_element_by_css_selector(".continue-button").click()

	def clickPlayNowButton(self):
		if self.driver.current_url == "http://www.muthead.com/gauntlet":
			self.driver.find_element_by_css_selector("button.button").click()
		else:
			if raw_input("Wrong page on clickPlayNowButton.  Retry? (Y/N) ").lower() == 'y':
				self.driver.find_element_by_css_selector("button.button").click()

	def choosePlayer(self, indexNum):
		#index num is the location on the screen
		selection = self.getCurrentPlayersOnScreen()[indexNum]
		cssSelector = genClass(selection)
		self.driver.find_element_by_css_selector(cssSelector).click()

	def getAnswerResult(self):
		return self.driver.find_element_by_css_selector(".result").get_attribute('innerHTML')

	def getCurrentScore(self):
		scoreElem = self.driver.find_element_by_css_selector(".stat-board .score").get_attribute('innerHTML')
		return re.findall('\d+', str(re.sub("(<!--.*?-->)", "", scoreElem, flags=re.MULTILINE)))[0]

if __name__ == '__main__':
	'''bot = startBot(loginType='twitch')
	bot.startGame()
	raw_input("Click Enter when the game begins Screen: ")
	while True:
		print("Running")
		try:
			bot.solveQuestionOnScreen()
			time.sleep(1)
			bot.clickContinueButton()
			time.sleep(2)
		except Exception as exp:
			print("Error")'''
	#grabAllPlayersNums()
	grabMoreInfoAboutPlayers()


