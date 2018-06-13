# -*- coding: utf-8 -*-
from __future__ import print_function

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


def set_task_in_session(intent, session):
    session_attributes = {}
    card_title = intent['name']
    should_end_session = False
    print('intent[slot]' + str(intent['slots']))
    if 'target' in intent['slots']:
        target = intent['slots']['target']['value']
        session_attributes = create_task_attributes(target)
        speech_output = target + \
                        "の時間を記録します。 " + \
                        "何時間ですか？"
        reprompt_text = "何時間記録しますか？"
    else:
        speech_output = "もう一度タスク名をはっきりと話してみてください。" \
                        "例えば　「ゆーちゅーぶの時間を記録して」　というふうに話してみてください"
        reprompt_text = "もう一度話してみてください"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def set_time_in_session(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    reprompt_text = ""

    print('intent[slot]' + str(intent['slots']))
    if 'time' in intent['slots'] and session.get('attributes', {}):
        time = intent['slots']['time']['value']
        task_name = session['attributes']['taskName']
        should_end_session = True
        speech_output = task_name + 'の時間を' + time + '時間記録しました。'
    else:
        speech_output = "もう一度時間をはっきりと話してみてください。" \
                        "例えば　「4時間」　というふうに話してみてください"
        reprompt_text = "もう一度話してみてください"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_color_from_session(intent, session):
    session_attributes = {}
    reprompt_text = None

    if session.get('attributes', {}) and "favoriteColor" in session.get('attributes', {}):
        favorite_color = session['attributes']['favoriteColor']
        speech_output = "Your favorite color is " + favorite_color + \
                        ". Goodbye."
        should_end_session = True
    else:
        speech_output = "I'm not sure what your favorite color is. " \
                        "You can say, my favorite color is red."
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
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
    if intent_name == "TimeManagementIntent":
        return set_task_in_session(intent, session)
    # 三時間
    elif intent_name == "RegistorTaskTimeIntent":
        return set_time_in_session(intent, session)
    # 今日のゆーちゅーぶの時間を教えて
    elif intent_name == "GetTimeIntent":
        return get_color_from_session(intent, session)
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
