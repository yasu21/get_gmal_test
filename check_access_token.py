from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import json

def get_creds():
	SCOPES = [
		'https://www.googleapis.com/auth/gmail.readonly',
		'https://www.googleapis.com/auth/gmail.modify'
	]

	# jsonファイルの読み込み
	with open("./env/token.json", "r") as json_file:
			info = json.load(json_file)

	creds = Credentials.from_authorized_user_info(info,SCOPES)
	print(f'有効か:{creds.valid}')
	print(f'期限切れか:{creds.expired}')
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			print('refresh')
			# アクセス トークンを更新
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file('./env/client_secret.json', SCOPES)
			creds = flow.run_local_server(port=0)
		with open('./env/token.json', 'w') as token:
			token.write(creds.to_json())
	else:
		print('creds:ok')

	print(f'有効期限:{creds.expiry}')
	return creds