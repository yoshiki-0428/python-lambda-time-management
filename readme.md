# TimeManagementApp from Alexa

# Description  
Alexaに自分の〇〇のタスクの時間を登録することができます。

- Conversation Example
1. 時間管理アプリを開いてゆーちゅーぶの時間を記録して
2. 四時間
3. 今日のゆーちゅーぶの時間を教えて

- Deploy
必要ツール
python3.6
pip3
python-lambda-local
lambda-uploader

- How to Deploy
lambda-uploader

- How to Execution Python
python-lambda-local -f lambda_handler lambda_function.py launch.json

- TODO
.gitignoreの追加
event.json系を外すべきか否か
dynamoDBの設定

