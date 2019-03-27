from __future__ import print_function
import json

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])
 
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

def on_session_started(session_started_request, session):
    """ Called when the session starts """
 
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])
 
 
def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
 
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()
 
 
def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """
 
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])
 
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
 
    # Dispatch to your skill's intent handlers
    #if intent_name == "foldor":
    #    return get_result(intent, session)
    if intent_name == "myHand":
        return configure_hand(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    else:
        raise ValueError("Invalid intent")
 
 
def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
 
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here
 
# --------------- Functions that control the skill's behavior ------------------
 
 
def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
 
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to ... Pocker Help. " \
                    "Please tell me your hand and I will advise you if you should keep it or fold "
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me your hand and I will advise you if you should keep it or fold "
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
 
def configure_hand(intent, session):
    
    value1 = intent['slots']['valueOne']['value']
    value2 = intent['slots']['valueTwo']['value']
    suit1 = intent['slots']['suitOne']['value']
    suit2 = intent['slots']['suitTwo']['value']
    
    # create a map for valueMap and suitMap where key is the string (from user input), and value is the right value for the code
    # for example {("Clubs", "C"), ("Hearts", "H")} but problems arise when alexa puts input in lowercase or uppercase.. need to check 
    suitMap = {
        "clubs": "C", 
        "hearts": "H", 
        "spades": "S", 
        "diamonds": "D"
    }
    
    valueMap = {
        "2":         2, 
        "3":         3, 
        "4":         4, 
        "5":         5,
        "6":         6,
        "7":         7,
        "8":         8,
        "9":         9,
        "10":       10,
        "jack":     11,
        "queen":    12,
        "king":     13,
        "ace":      14,
    }
    # check if value1 == valueMap.key then value1 = valueMap.value
    for item in suitMap: 
        if (item == suit1): 
            suit1 = suitMap.get(item)
        else: 
            # return error handler
        if (item == suit2):
            suit2 = suitMap.get(item)
        else: 
            # return error handler 

        
    for item in valueMap:
        if (item == value1):
            value1 = valueMap.get(item)
        else: 
            # return error handler
        if (item == value2):
            value2 = valueMap.get(item)
        else: 
            # return error handler 
        
    ''' then create card 1 and card 2 '''
    card1 = Card(value1, suit1)
    card2 = Card(value2, suit2)
    
    ''' then find the rank of the hand ''' 
    rank_of_hand = countRank(card1, card2)
    
    ''' then find the statistics '''
    return get_result(rank_of_hand, intent)
    # sessionAttributes ={}
    # card_title = "Response"
    # speech_output = "okay oleg dalodnd"
    # reprompt_text = " fika"
    # should_end_session = True
    # return build_response(session_attributes, build_speechlet_response(
    #     card_title, speech_output, reprompt_text, should_end_session))

def makeRankArray():
    RankArray1 = []
    for i in range(len(value)):
        for j in range(len(value)):
            if (i==j):
                RankArray1.append((value[i]*10000+value[i]*100+value[i]))
            elif (j > i):
                RankArray1.append((value[i]*1000)+(value[j]*10))
                RankArray1.append(int(((value[i]*1000)+(value[j]*10))*1.12))
    return RankArray1
RankArray = makeRankArray()
RankArray.sort()
RankArray.reverse()
def countRank(card1,card2):
        # in case of pocket pair
        if (card1.value == card2.value):
            # the index from value [] +1 equals rank 
            return RankArray.index((card1.value*10000) + (card1.value*100) + (card1.value))+1
        # in case of non-paired suited hands
        elif (card1.suit == card2.suit):
            if (card1.value > card2.value):
                return RankArray.index(int(((card1.value*1000) + (card2.value*10))*1.12) )+1
            else:
                return RankArray.index(int(((card2.value*1000) + (card1.value*10))*1.12 ))+1
        else:
            if (card1.value > card2.value):
                return RankArray.index((card1.value*1000) + (card2.value*10))+1
            else:
                return RankArray.index((card2.value*1000) + (card1.value*10))+1

class Card():
    def __init__(self,value,suit):
        self.value = value
        self.suit = suit

def get_result(rank, intent): 
    card_title = intent['name']
    session_attributes = {}
    result = False
    
    percents = (float(rank)/float(169))
    if ((float(rank)/float(169))>0.35):
        result = True
    else:
        result = False
    
    
    if (result == True):
        speech_output = "There are {:.2%} of hands that are better than yours, I advise you to fold".format(percents) \
 
        reprompt_text = ""
    elif (result == False):  
        speech_output = "You have a good hand, you should keep it!" \
        
        reprompt_text = ""
    else:
        speech_output = "Please tell me your hand"
        reprompt_text = "Please tell me your hand"
    
    should_end_session = True  #maybe false
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
# --------------- Helpers that build all of the responses ----------------------
 
 
def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
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
    
