from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import time
import glob
from datetime import datetime
import configparser

config = configparser.ConfigParser()
config.read('para.ini')

CSV_FOLDER  = config['PATH']['CSV_FOLDER']
DRIVER_PATH = config['PATH']['DRIVER_PATH']
USER_ID     = config['TWITTER']['USER_ID']
PASSWORD    = config['TWITTER']['PASSWORD']


def download_option():
	if os.path.isdir(CSV_FOLDER):
		pass
	else:
		os.mkdir(CSV_FOLDER)
		
	chrome_option = webdriver.ChromeOptions()
	prefs = {"download.default_directory": CSV_FOLDER}
	chrome_option.add_experimental_option("prefs", prefs)
	
	return chrome_option


def login_twitter(driver):
	driver.get('https://analytics.twitter.com/user/{}/tweets'.format(USER_ID))
	assert 'Twitter' in driver.title
	
	id_field = driver.find_element_by_class_name('js-username-field')
	pass_field = driver.find_element_by_class_name('js-password-field')
	
	id_field.send_keys(USER_ID)
	pass_field.send_keys(PASSWORD)
	pass_field.send_keys(Keys.RETURN)
	return


def csv_range_selection(driver):
	range_selection_button = driver.find_element_by_xpath('/html/body/div[2]/div/div[2]/div')
	range_selection_button.click()
	driver.implicitly_wait(10)
	
	past7days = driver.find_element_by_xpath('/html/body/div[4]/div[4]/ul/li[1]')
	past7days.click()
	driver.implicitly_wait(10)
	return


def download_csv(driver):
	export_button = driver.find_element_by_xpath('//*[@id="export"]/button')
	export_button.click()
	
	# DLが始まるまで待つ,始まったらファイル名を取り出す
	file = ''
	while True:
		if glob.glob(CSV_FOLDER + '/tweet_activity_metrics*'):
			file = glob.glob(CSV_FOLDER + '/tweet_activity_metrics*')[0]
			break

	# DLが完了するまで待つ
	while os.stat(file).st_size == 0:
		time.sleep(1)

	now = datetime.now().strftime("%Y-%m-%d_%H-%M")
	# ここでのリネームは、DL完了判定上の便宜も兼ねている
	os.rename(file, str(CSV_FOLDER + '/scraped_{}.csv'.format(now)))
	return


def main():
	chrome_option = download_option() # CSV_FOLDER にダウンロードするようにしたchromeの設定ファイル
	driver = webdriver.Chrome(executable_path=DRIVER_PATH, chrome_options=chrome_option)
	
	login_twitter(driver)
	
	csv_range_selection(driver)  # twitterを操作してcsvの範囲指定 : 過去7日間
	
	print('> try download csv')
	download_csv(driver)  # csvを指定フォルダにDL
	print('> downloaded csv successfully')
	
	driver.quit()
	try:
		driver.close()
	except ConnectionRefusedError:  # closeすると確実にこうなるので
		pass
	return


if __name__ == '__main__':
	main()