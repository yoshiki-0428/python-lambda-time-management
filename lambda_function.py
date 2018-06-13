import json

def lambda_handler(event, context):
    print("start")
    print("id:" + event['id'])
    print("product:" + event['product'])
    print("sex:" + event['sex'])
    print("price:" + event['price'])
