#!/usr/bin/env python

import urllib2
import json
import datetime
import sys


def call_api_ng(jsonrpc_req):
    try:
        req = urllib2.Request(url, jsonrpc_req, headers)
        response = urllib2.urlopen(req)
        jsonResponse = response.read()
        return jsonResponse
    except urllib2.URLError:
        raise Exception('Oops no service available at %s' % url)
    except urllib2.HTTPError:
        raise Exception('Oops not a valid operation from the service %s' % url)


def get_event_types():
    event_type_req = '{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listEventTypes", "params": {"filter":{ }}, "id": 1}'
    print 'Calling listEventTypes to get event Type ID'
    event_types_response = call_api_ng(event_type_req)
    event_type_loads = json.loads(event_types_response)
    print event_type_loads
    return event_type_loads['result']


def get_event_type_id_for_event_type_name(event_types_result, requested_event_type_name):
    if not event_types_result:
        raise Exception("No results")

    for event in event_types_result:
        event_type_name = event['eventType']['name']
        if event_type_name == requested_event_type_name:
            return  event['eventType']['id']


"""
Calling marketCatalouge to get marketDetails
"""

def get_market_catalogue_for_next_gb_win(event_type_id):
    if not event_type_id:
        return

    print 'Calling listMarketCatalouge Operation to get MarketID and selectionId'
    now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    market_catalogue_req = '{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listMarketCatalogue", "params": {"filter":{"eventTypeIds":["' + event_type_id + '"],"marketCountries":["GB"],"marketTypeCodes":["WIN"],'\
                                                                                                                                                         '"marketStartTime":{"from":"' + now + '"}},"sort":"FIRST_TO_START","maxResults":"1","marketProjection":["RUNNER_METADATA"]}, "id": 1}'
    market_catalogue_response = call_api_ng(market_catalogue_req)
    market_catalogue_loads = json.loads(market_catalogue_response)
    try:
        market_catalogue_results = market_catalogue_loads['result']
        return market_catalogue_results
    except:
        raise Exception('Exception from API-NG' + str(market_catalogue_results['error']))

def get_market_id(market_catalogue_result):
    for market in market_catalogue_result:
        return market['marketId']
    raise Exception("no marketId")

def get_selection_id(market_catalogue_result):
    for market in market_catalogue_result:
        return market['runners'][0]['selectionId']


def get_market_book_best_offers(marketId):
    print 'Calling listMarketBook to read prices for the Market with ID :' + marketId
    market_book_req = '{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listMarketBook", "params": {"marketIds":["' + marketId + '"],"priceProjection":{"priceData":["EX_BEST_OFFERS"]}}, "id": 1}'
    """
    print  market_book_req
    """
    market_book_response = call_api_ng(market_book_req)
    """
    print market_book_response
    """
    market_book_loads = json.loads(market_book_response)
    try:
        market_book_result = market_book_loads['result']
        return market_book_result
    except:
        print  'Exception from API-NG' + str(market_book_result['error'])
        exit()


def print_price_info(market_book_result):
    if(market_book_result is not None):
        print 'Please find Best three available prices for the runners'
        for marketBook in market_book_result:
            runners = marketBook['runners']
            for runner in runners:
                print 'Selection id is ' + str(runner['selectionId'])
                if (runner['status'] == 'ACTIVE'):
                    print 'Available to back price :' + str(runner['ex']['availableToBack'])
                    print 'Available to lay price :' + str(runner['ex']['availableToLay'])
                else:
                    print 'This runner is not active'


def placeFailingBet(marketId, selectionId):
    if( marketId is not None and selectionId is not None):
        print 'Calling placeOrder for marketId :' + marketId + ' with selection id :' + str(selectionId)
        place_order_Req = '{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/placeOrders", "params": {"marketId":"' + marketId + '","instructions":'\
                                                                                                                              '[{"selectionId":"' + str(
            selectionId) + '","handicap":"0","side":"BACK","orderType":"LIMIT","limitOrder":{"size":"0.01","price":"1.50","persistenceType":"LAPSE"}}],"customerRef":"test12121212121"}, "id": 1}'
        """
        print place_order_Req
        """
        place_order_Response = call_api_ng(place_order_Req)
        place_order_load = json.loads(place_order_Response)
        try:
            place_order_result = place_order_load['result']
            print 'Place order status is ' + place_order_result['status']
            """
            print 'Place order error status is ' + place_order_result['errorCode']
            """
            print 'Reason for Place order failure is ' + place_order_result['instructionReports'][0]['errorCode']
        except:
            print  'Exception from API-NG' + str(place_order_result['error'])
        """
        print place_order_Response
        """


url = "https://api.betfair.com/exchange/betting/json-rpc/v1"

"""
headers = { 'X-Application' : 'coxsim', 'X-Authentication' : 'GO3cA7sDLExqPatk' ,'content-type' : 'application/json' }
"""

args = len(sys.argv)

if ( args < 3):
    print 'Please provide Application key and session token'
    appKey = raw_input('Enter your application key :')
    sessionToken = raw_input('Enter your session Token/SSOID :')
    print 'Thanks for the input provided'
else:
    appKey = sys.argv[1]
    sessionToken = sys.argv[2]

headers = {'X-Application': appKey, 'X-Authentication': sessionToken, 'content-type': 'application/json'}

event_types_result = get_event_types()
horse_racing_event_type_id = get_event_type_id_for_event_type_name(event_types_result, 'Horse Racing')

print 'Eventype Id for Horse Racing is :' + str(horse_racing_event_type_id)

marketCatalogueResult = get_market_catalogue_for_next_gb_win(horse_racing_event_type_id)
market_id = get_market_id(marketCatalogueResult)
runner_id = get_selection_id(marketCatalogueResult)
market_book_result = get_market_book_best_offers(market_id)
print_price_info(market_book_result)

placeFailingBet(market_id, runner_id)


