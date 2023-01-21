import base64
import json
from googleapiclient.discovery import build
from check_access_token import get_creds
from datetime import datetime

try:
    creds=get_creds()
except:
    print('認証失敗')

# Gmail APIを使用して、Gmailのサービスを構築します。
service = build('gmail', 'v1', credentials=creds)

# 受信トレイからメッセージを取得します。特定ラベルの受信メッセージを1件取得
# jsonファイルの読み込み
with open("./env/setting.json", "r") as json_file:
    setting= json.load(json_file)
label_id=setting['label_id']
max=setting['max']
results = service.users().messages().list(userId='me', labelIds=[label_id], q='is:unread',maxResults=max).execute()
messages = results.get('messages', [])

def get_header(headers, name):
    for h in headers:
        if h['name'].lower() == name:
            return h['value']

def base64_decode(data):
    return base64.urlsafe_b64decode(data).decode()

def get_body(message):
    data=message['snippet']
    # 本文を取得
    if 'parts' in message['payload']:
        parts = message['payload']['parts']
        if parts[0]['body']['size'] > 0:
            data = base64_decode(parts[0]['body']['data'])
    else:
        data = base64_decode(message['payload']['body']['data'])
    return data

def get_file_name(message):
    names=[]
    # 添付ファイルのファイル名を取得
    if 'parts' in message['payload']:
        parts = message['payload']['parts']
        for part in parts:
            if part['filename']:
                names.append(part['filename'])
    else:
        if message['payload']['filename']:
            names.append(message['payload']['filename'])
    return names

def format_date(str_date):
    # 文字列を datetime オブジェクトに変換
    if "+" in str_date or "-" in str_date:
        date_time = datetime.strptime(str_date, '%a, %d %b %Y %H:%M:%S %z')
    else:
        date_time = datetime.strptime(str_date, '%a, %d %b %Y %H:%M:%S %Z')
    # 指定したフォーマットに変換
    formatted_date_time = date_time.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_date_time

def update_readed(id):
    service.users().messages().modify(userId='me', id=id, body={'removeLabelIds': ['UNREAD']}).execute()

for msg in messages:
    m_data = service.users().messages().get(userId='me',id=msg['id']).execute()

    # ヘッダー情報
    headers = m_data['payload']['headers']

    # 差出人
    from_date = get_header(headers, 'from')
    print(f'差出人: {from_date}')

    # 日付
    message_date = get_header(headers, 'date')
    date=format_date(message_date)
    print(f'日付: {date}')

    # 件名
    sub_date = get_header(headers, 'subject')
    print(f'件名: {sub_date}')

    # 本文
    message = service.users().messages().get(userId='me', id=msg['id']).execute()
    body=get_body(message)
    print(f'本文: {body}')

    #添付ファイル名
    names=get_file_name(message)
    length=len(names)
    print(f'添付ファイル:{length}件')
    for name in names:
        print(f'ファイル名: {name}')

    #既読にする
    update_readed(msg['id'])
