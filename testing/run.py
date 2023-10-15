import time
import re
import sys

from selenium import webdriver
# from selenium.webdriver.chrome.service import Service as ChromiumService
# from webdriver_manager.chrome import ChromeDriverManager
# from webdriver_manager.core.os_manager import ChromeType




def get_link(string, pattern = '(suckhoe)(.*)(html)'):
	result = re.findall(pattern, string)
	return "".join(list(result[0]))


def read_txt(data_path):
	with open(data_path, "r") as f:
		data = f.readlines()

	list_url = []
	for line in data:
		line = line.strip()
		list_url.append(line)

	return list_url


def release(webBrowser, list_url, instance_per_round = 30, num_round = 30, delay = 0.2):
	webBrowser.get("http://google.com")
	for idx, url in enumerate(list_url):
		print('\nURL: ', url)
		try:
			for rou in range(num_round):
				# webBrowser.switch_to_window(webBrowser.window_handles[0])
				webBrowser.switch_to.window(webBrowser.window_handles[0])
				for idx in range(instance_per_round):
					webBrowser.execute_script("window.open()")
					# webBrowser.switch_to_window(webBrowser.window_handles[idx + 1])
					webBrowser.switch_to.window(webBrowser.window_handles[idx + 1])
					webBrowser.get(url)
					# webBrowser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
					for i in range(5):
						time.sleep(1)
						js = "window.scrollTo(window.scrollY, window.scrollY + window.innerHeight);"
						webBrowser.execute_script(js)
					time.sleep(delay)

				for idx in range(instance_per_round):
					# webBrowser.switch_to_window(webBrowser.window_handles[instance_per_round - idx])
					webBrowser.switch_to.window(webBrowser.window_handles[instance_per_round - idx])
					webBrowser.close()
					time.sleep(delay)

				time.sleep(1)
		except:
			print('Link lỗi')


if __name__ == "__main__":
	# list_url = ["https://www.bing.com/", "https://www.bing.com/", "https://www.bing.com/"]

	drive_path = "./drive/chromedriver"
	webBrowser = webdriver.Chrome(drive_path)

	# drive_path = "C:/Users/binht/Downloads/Click_Multi_Tabs/drive/chromedriver"
	# service = webdriver.ChromeService(executable_path = (drive_path))

	# webBrowser = webdriver.Chrome(service=ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()))


	# drive_path = "./drive/geckodriver"
	# webBrowser = webdriver.Firefox(drive_path)

	data_path = sys.argv[1]		# "./data.txt"	
	
	instance_per_round = 35	# Số tab mở một lượt (sau đó tắt hết đi để mở lại, giảm tải cho trình duyệt)
	num_round = 2				# Số lượt mở 
	delay = 0					# Thời gian chờ để mở tab mới, đơn vị giây (cần thời gian chờ để tải trang)

	list_url = read_txt(data_path)
	release(webBrowser, list_url, instance_per_round, num_round, delay)



	### pip install selenium==3.14.0