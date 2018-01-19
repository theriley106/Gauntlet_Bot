import requests
import bs4
import threading
import re
import traceback
import json
import time
from selenium import webdriver
# only for Madden 18 rn

def grabSite(url, retry=False):
	failCount = 0
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
	res = requests.get(url, headers=headers)
	while res.status_code != 200 and failCount < 5 and retry == True:
		print("Network Failed: {}".format(url))
		# this will reattempt to grab the page 5 times if you specify retry as true
		res = requests.get(url, headers=headers)
	return res

def genClass(playNum):
	return '.instance_card_{}'.format(playNum)

def grabAllPlayersNums(verbose=True, saveAs="database.json"):
	#This grabs every player number from Muthead - it generates that primaryDB.json
	playerDB = []
	for pageNum in range(1,214):
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

	def getCurrentPlayersOnScreen(self):
		htmlElement = self.driver.find_element_by_css_selector(".gauntlet-choices").get_attribute('innerHTML')
		cardsOnScreen = re.findall("\sinstance_card_(\d+)", str(htmlElement))
		if len(cardsOnScreen) == 3:
			return cardsOnScreen
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

	def clickContinueButton(self):
		self.driver.find_element_by_css_selector(".continue-button").click()

	def clickPlayNowButton(self):
		if self.driver.current_url == "http://www.muthead.com/gauntlet":
			driver.find_element_by_css_selector("button.button").click()
		else:
			if raw_input("Wrong page on clickPlayNowButton.  Retry? (Y/N) ").lower() = 'y':
				driver.find_element_by_css_selector("button.button").click()

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


#def grabPlayerInfo():

#def grabAllInfo():
	
	#Grabs page_1 to page_213
	#grabSite('http://www.muthead.com/18/players')


#login type can either be "curse" or "twitch"
if __name__ == '__main__':
	username = 'yaaaaaaaboy'
	bot = startBot(loginType='twitch', username=username, password='parkerddog10616')
	bot.startGame()
	bot.clickPlayNowButton()
	#grabAllPlayersNums()
	'''res = grabSite("http://www.muthead.com/18/players/{}/full-ratings".format(raw_input("Player number: ")))
	page = bs4.BeautifulSoup(res.text, 'lxml')
	print page.title.string
	#print page.select("#content")
	for val in page.select(".player-details-stats span"):
		print val.getText()'''
	#res = grabSite(url)
	#page = bs4.BeautifulSoup(res.text, 'lxml')


