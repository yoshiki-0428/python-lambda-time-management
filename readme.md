## TimeManagementApp from Alexa

#### Description
Alexaに自分の〇〇のタスクの時間を登録することができます。

- Conversation Example(会話の例)
1. 時間管理アプリを開いてyoutubeの時間を記録して
2. 四時間
3. 今日のyoutubeの時間を教えて

##### Need Tools
- python3.6
- pip(3)
- [dynamoDB local](http://dynamodb-local.s3-website-us-west-2.amazonaws.com/dynamodb_local_latest.zip)
 [(how to)](https://qiita.com/Hiroki11x/items/756797b45d4461784013)

##### How to Deploy
1. aws configure
2. Set your aws configure
3. [lambda-uploader](https://dev.classmethod.jp/cloud/deploy-aws-lambda-python-with-lambda-uploader/)

##### How to local execution lambda
python-lambda-local --function lambda_handler --timeout 5 aws_lambda/main.py aws_lambda/event/launch.json

###### TODO
- event.json系を外すべきか否か
- dynamoDBの設定

