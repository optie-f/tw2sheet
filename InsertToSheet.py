import pandas as pd
import os
import httplib2
from datetime import datetime
from googleapiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from pprint import pprint
import glob
import configparser

config = configparser.ConfigParser()
config.read('para.ini')

try:
	import argparse
	flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
	flags = None
 

SCOPES = config['GOOGLE']['SCOPES']
CLIENT_SECRET_FILE = config['GOOGLE']['CLIENT_SECRET_FILE']
APPLICATION_NAME = config['GOOGLE']['APPLICATION_NAME']

CSV_FOLDER = config['PATH']['CSV_FOLDER']

SPREADSHEET_ID = config['SHEET']['SPREADSHEET_ID']
SHEET_NAME = config['SHEET']['SHEET_NAME']


def get_credentials():
	home_dir = os.path.expanduser('~')
	credential_dir = os.path.join(home_dir, '.credentials')
	
	if not os.path.exists(credential_dir):
		os.mkdir(credential_dir)
	
	credential_path = os.path.join(credential_dir,
	                               'sheets.googleapis.com-python-quickstart.json')
	
	store = Storage(credential_path)
	credentials = store.get()
	
	if not credentials or credentials.invalid:
		flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
		flow.user_agent = APPLICATION_NAME
		if flags:
			credentials = tools.run_flow(flow, store, flags)
		else:
			credentials = tools.run(flow, store)
		print('Storing credentials to ' + credential_path)
	
	return credentials


def get_service_instance(credentials):
	http = credentials.authorize(httplib2.Http())
	discoveryUrl = 'https://sheets.googleapis.com/$discovery/rest?''version=v4'
	service = discovery.build('sheets', 'v4', http=http,
	                          discoveryServiceUrl=discoveryUrl)
	return service


def pre_process():
	file = glob.glob(CSV_FOLDER + '/scraped_*')[0]
	df = pd.read_csv(file)
	
	df.index = pd.DatetimeIndex(pd.to_datetime(df['時間']), name='時間').tz_localize('UTC').tz_convert('Asia/Tokyo')
	df['時間'] = df.index
	df = df.reset_index(drop=True)
	
	# datetimeのままだと tolist() した時に Timestamp に変換されJSONで扱えなくなったので文字列化
	df['時間'] = df['時間'].dt.strftime('%Y-%m-%d %H:%M:%S')
	# どこかでIDがfloatに化けたのでstringにしておく
	df['ツイートID'] = df['ツイートID'].astype('str')
	
	now = datetime.now().strftime("%Y-%m-%d_%H-%M")
	# import完了判定
	os.rename(file, str(CSV_FOLDER + '/imported_{}.csv'.format(now)))
	
	return df


def insert_df_to_sheet(df, service):
	# 列名の行が存在するかどうか =
	range = SHEET_NAME + '!' + '1:1'
	column_check = service.spreadsheets().values().get(
		spreadsheetId=SPREADSHEET_ID, range=range).execute()
	columns = column_check.get('values', [])
	
	if not columns:
		cols = [df.columns.tolist()]
		vals = df.as_matrix().tolist()
		array = cols + vals
		print(array)
	else:
		array = df.as_matrix().tolist()
	
	value_range_body = {
		"range": "A1:B2",
		"majorDimension": "ROWS",
		"values": array,
	}
	value_input_option = 'USER_ENTERED'  # '%Y-%m-%d %H:%M:%S'をDatetimeとして入力させるため
	insert_data_option = 'INSERT_ROWS'
	range_ = 'A1:B2'
	
	request = service.spreadsheets().values().append(spreadsheetId=SPREADSHEET_ID,
	                                                 range=range_,
	                                                 valueInputOption=value_input_option,
	                                                 insertDataOption=insert_data_option,
	                                                 includeValuesInResponse=True,
	                                                 body=value_range_body)
	
	response = request.execute()
	
	pprint(response)
	
	return


def test(service):
	rangeName= 'A1:C24'
	range = SHEET_NAME + '!' + rangeName
	
	test = service.spreadsheets().values().get(
		spreadsheetId=SPREADSHEET_ID, range=range).execute()
	
	values = test.get('values', [])
	
	if not values:
		print('No data found')
	else:
		for row in values:
			print(row)
	
	return


def main():
	credentials = get_credentials()  # 認証情報ファイルを参照, なければ取得してくる
	service = get_service_instance(credentials)  # APIにアクセスするためのインスタンス
	
	df = pre_process()  # pandasで前処理(今回はUTC→JST補正のみ)
	
	insert_df_to_sheet(df, service)
	
	return


if __name__ == '__main__':
	main()