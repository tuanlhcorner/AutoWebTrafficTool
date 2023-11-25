import time
import re
import sys
import urllib

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager



class Core(object):
	def __init__(self, browser="Firefox",
			  		instance_per_round = 1,
					num_round = 1,
					delay = 0.2) -> None:
		# self.webBrowser = self.browserConnector(browser)
		self.partner = ""			# '(suckhoe)(.*)(html)'

		self.instance_per_round = instance_per_round
		self.num_round = num_round
		self.delay = delay

		self.urls = []

	def update_partner(self, partner):
		self.partner = partner

	def check_url(self, url):
		try:
			if urllib.request.urlopen(url).getcode() == 200:
				return True
			return False
		except:
			return False

	def browserConnector(self, btype='Firefox'):
		done = False
		while not done:
			try:
				if btype == 'Firefox':
					webBrowser = webdriver.Firefox()
					done = True
				elif btype == 'Chrome':
					service = Service(ChromeDriverManager().install())
					webBrowser = webdriver.Chrome(service=service)
				# webBrowser.close()
				return webBrowser

			except Exception as e:
				btype = 'Firefox'
				message = f"ERROR > {e}"

		return None

	def get_link(self, string):
		result = re.findall(self.pattern, string)
		return "".join(list(result[0]))
	
	def data_info(self):
		info = {}
		if self.urls:
			length = len(self.urls)
			domains = [urllib.parse.urlparse(url).netloc for url in self.urls]
			domains = list(set(d for d in domains if d != ""))

			live_urls = [url for url in self.urls if self.check_url(url)]
			live_urls = []
			die_urls = []
			for url in self.urls:
				if self.check_url(url):
					live_urls.append(url)
				else:
					die_urls.append(url)

			info = {
				"length": length,
				"domain_list": domains,
				"live_urls": live_urls,
				"die_urls": die_urls
			}
		return info

	def read(self, path=""):
		if not path or not path.endswith("txt"):
			return None

		with open(path, "r") as f:
			data = f.readlines()

		result = [line.strip() for line in data]
		self.urls = result


	def test_release(self, urls = None):
		length = len(urls)
		for idx, url in enumerate(urls):
			time.sleep(1)
			yield {
				"success": True,
				"url": url, 
				"step":int((idx+1)*100/length),
				"message": "testing"
			}

	def release(self, urls = None):
		# checking web browser is available
		# if not self.webBrowser:
		# 	return

		# self.webBrowser.get("http://google.com")			# init
		length = len(urls)

		for idx, url in enumerate(urls):
			if not self.check_url(url):
				yield {
					"success": False,
					"url": url,
					"message": "URL is unvailable"
				}
			try:
				msg = "Thanh cong"
				# for rou in range(self.num_round):
				# 	self.webBrowser.switch_to.window(self.webBrowser.window_handles[0])
				# 	for idx in range(self.instance_per_round):
				# 		self.webBrowser.execute_script("window.open()")
				# 		self.webBrowser.switch_to.window(self.webBrowser.window_handles[idx + 1])
				# 		self.webBrowser.get(url)

				# 		for i in range(5):
				# 			time.sleep(1)
				# 			js = "window.scrollTo(window.scrollY, window.scrollY + window.innerHeight);"
				# 			self.webBrowser.execute_script(js)

				# 		time.sleep(self.delay)

				# 	for idx in range(self.instance_per_round):
				# 		self.webBrowser.switch_to.window(self.webBrowser.window_handles[self.instance_per_round - idx])
				# 		self.webBrowser.close()
				# 		time.sleep(self.delay)

				time.sleep(1)
			except:
				msg = 'Link lỗi'
			
			yield {
				"success": True,
				"url": url, 
				"step":int((idx+1)*100/length),
				"message": msg
			}

