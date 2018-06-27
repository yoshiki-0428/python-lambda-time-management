# -*- coding: utf-8 -*-
from __future__ import print_function
import boto3
from boto3.dynamodb.conditions import Key
from aws_lambda.helper import DecimalEncoder
import datetime
import json

# --------------- Main handler ------------------
def lambda_handler(event, context):
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


# --------------- DB Put Query Access ------------------
def db_access(task_name, time):
    today = str(datetime.date.today())
    time = int(time)

    # TODO ユーザの確認 & 例外処理
    response = get_json_from_db("yoshiki")

    # dynamoDBの値はユニコード化されて送られてくるので変換が必要
    for i in response[u'Items']:
        json.dumps(i, cls=DecimalEncoder)
    # DBの値はItemsの0番目に格納されている
    response = response['Items'][0]

    print("##### db response debug #####")
    print(type(response))
    print(response)
    print("#################")

    tasks = []
    if type(response['task'] == list):
        for task in response['task']:
            tasks.append(task['value'])

    # タスクが存在しない場合に追加
    if len(response['task']) == 0:
        print("##### no task #####")
        response['task'] = [{
            "date": [create_date_json(today, time)],
            "value": task_name
        }]

    # タスクがすでに存在する場合
    elif task_name in tasks:
        print("##### task contain #####")
        # 指定のタスクに日時と経過時間を追加
        for date in response['task']:
            if date['value'] == task_name:
                dates = create_dates(date)
                # 当日のデータあり
                if today in dates:
                    for v in date['date']:
                        if v['date'] == today:
                            v['date'] = today
                            v['used_time'] = time
                            print("#### show dates")
                            print(v)

                # 当日のデータなし
                else:
                    date['date'].append(create_date_json(today, time))

    # 未登録のタスクがある場合
    else:
        print("##### don't register task #####")
        response['task'].append({
            "date": [create_date_json(today, time)],
            "value": task_name
        })

    print("#### open response #####")
    print(response)
    print("########################")
    put_json_to_db(response)


def create_dates(date):
    dates = []
    for v in date['date']:
        dates.append(v['date'])
    return dates


def put_json_to_db(json):
    dynamoDB = boto3.resource("dynamodb")
    table = dynamoDB.Table("time_management")

    # DynamoDBへのPut処理実行
    table.put_item(Item=json)


def get_json_from_db(user_id):
    dynamoDB = boto3.resource("dynamodb")
    table = dynamoDB.Table("time_management")

    # DynamoDBへのGet処理実行
    query_data = table.query(
        KeyConditionExpression=Key("user_id").eq(user_id),
        Limit=1
    )
    return query_data


def get_task_time_from_db(target, date = None, user_id = "yoshiki"):
    dynamoDB = boto3.resource("dynamodb")
    table = dynamoDB.Table("time_management")

    # DynamoDBへのGet処理実行
    query_data = table.query(
        KeyConditionExpression=Key("user_id").eq(user_id),
        Limit=1
    )

    return query_data


def get_time_by_target(target, target_date = None):
    response = get_json_from_db("yoshiki")
    # dynamoDBの値はユニコード化されて送られてくるので変換が必要
    for i in response[u'Items']:
        json.dumps(i, cls=DecimalEncoder)
    # DBの値はItemsの0番目に格納されている
    response = response['Items'][0]

    # 今週だった場合
    target_date_array = []
    if target_date.find("W") != -1:
        for i in range(7):
            date = datetime.date.today() - datetime.timedelta(days=i)
            target_date_array.append(str(date))

    else:
        target_date_array.append(target_date)

    print(target_date_array)

    count = 0
    task = search_task_by_target(response, target)

    for date in task['date']:
        if date['date'] in target_date_array:
            count = count + int(date['used_time'])
    print("###### show count")
    print(count)
    return count


def search_task_by_target(response, target):
    for task in response['task']:
        if task['value'] == target:
            return task

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "ようこそ時間管理アプリへ" \
                    "あなたの登録したいタスクを話しかけてみてください。" \
                    "例えば、こんなふうに「時間管理アプリを開いて、ゆーちゅーぶの時間を記録して」"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "もう一度話しかけてみてください。"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Skills Kit sample. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def create_task_attributes(target):
    return {"taskName": target}


def create_date_json(today, time):
    return {
        "date": today,
        "used_time": time
    }


def set_task_in_session(intent, session):
    session_attributes = {}
    card_title = intent['name']
    should_end_session = False
    print('intent[slot]' + str(intent['slots']))

    if 'target' in intent['slots']:
        target = intent['slots']['target']['value']
        session_attributes = create_task_attributes(target)
        speech_output = target + "の時間を記録します。何時間ですか？"
        reprompt_text = "何時間記録しますか？"

    else:
        speech_output = "もう一度タスク名をはっきりと話してみてください。" \
                        "例えば　「ゆーちゅーぶの時間を記録して」　というふうに話してみてください"
        reprompt_text = "もう一度話してみてください"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def set_time_in_session(intent, session):
    card_title = intent['name']
    session_attributes = session['attributes']
    should_end_session = False
    reprompt_text = ""

    print('intent[slot]' + str(intent['slots']))
    if 'time' in intent['slots'] and session.get('attributes', {}):
        time = intent['slots']['time']['value']
        # add time to the session
        session['attributes']['time'] = time
        session_attributes = session['attributes']
        task_name = session['attributes']['taskName']
        should_end_session = False
        speech_output = task_name + 'の時間を' + time + '時間記録しました。'
        db_access(task_name, time)

    else:
        speech_output = "もう一度時間をはっきりと話してみてください。" \
                        "例えば　「4時間」　というふうに話してみてください"
        reprompt_text = "もう一度話してみてください"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_time_from_json(intent, session):
    session_attributes = {}
    reprompt_text = None

    if (intent.get("slots", {}) and
            intent['slots'].get("date", {}) and
            intent['slots'].get("target", {})):

        # get the slots
        slots  = intent['slots']
        date   = slots['date']['value']
        target = slots['target']['value']

        # task_name = session['attributes']['taskName']
        # time     = session['attributes']['time']
        print("##### show iso date")
        print(type(date))
        print(date)

        time = get_time_by_target(target, date)
        if date.find("W") == -1:
            speech_output = date + "の" + target + "に使用した時間は" + str(time) + "時間です。"
        else:
            speech_output = "今週の" + target + "に使用した時間は" + str(time) + "時間です。"

        should_end_session = True

    else:
        speech_output = "もう一度話してみてください。"
        should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    print('intent_name ===' + intent_name)

    # ゆーちゅーぶの時間を記録して
    if intent_name == "RegisterTaskIntent":
        return set_task_in_session(intent, session)
    # 三時間
    elif intent_name == "RegisterTimeIntent":
        return set_time_in_session(intent, session)
    # 今日のゆーちゅーぶの時間を教えて
    elif intent_name == "GetTimeIntent":
        return get_time_from_json(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here