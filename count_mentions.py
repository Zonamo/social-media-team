from datetime import datetime, time, timedelta
import time
import tweepy
import json
import os
import sys
from discord import Webhook, RequestsWebhookAdapter

def json_handler():
    with open(os.path.join(sys.path[0], 'sheet.txt'), 'r') as file:
        string = file.read()
        data = json.loads(string)    
    return data

def get_client(bearer):
    client = tweepy.Client(bearer_token=bearer)
    return client

def get_all_bearers():
    with open(os.path.join(sys.path[0], 'bearers_mentions.json'), 'r') as file:
        string = file.read()
        bearer_list = json.loads(string) 
    return bearer_list

def get_bearer(spot):
    bearer_list = get_all_bearers()
    print(f'spot mention: {spot}')
    print(f'len: {len(bearer_list)}')
    now = datetime.utcnow()
    now = datetime.strptime(str(now), '%Y-%m-%d %H:%M:%S.%f')
    now = now.replace(microsecond=0)
    unix_now = time.mktime(now.timetuple())
    unix_now = int(format(unix_now, '.0f'))
    if spot == len(bearer_list):
        spot = 0
    while spot < len(bearer_list):
        bearer_info = bearer_list[spot]
        rate_count = bearer_info[0]
        bearer_token = bearer_info[1]
        if rate_count + 900 < unix_now:
            break
        spot += 1
        if spot == len(bearer_list):
            spot = 0
    print(f'spot mention give: {spot}')
    return bearer_token, spot
            
def update_bearer(bearer_spot, faulty):
    if faulty == 0:
        now = datetime.utcnow()
        now = datetime.strptime(str(now), '%Y-%m-%d %H:%M:%S.%f') - timedelta(seconds=10)
        now = now.replace(microsecond=0)
        unix_now = time.mktime(now.timetuple())
        unix_now = int(format(unix_now, '.0f'))
    if faulty == 1:
        unix_now = 66600000000
    with open(os.path.join(sys.path[0], 'bearers_mentions.json'), 'r') as file:
        string = file.read()
        bearer_list = json.loads(string) 
        bearer_list[bearer_spot][0] = unix_now
        with open(os.path.join(sys.path[0],"bearers_mentions.json"), "w") as file:
            file.write(json.dumps(bearer_list))
    return
        
def new_bearer(old_spot, faulty):
    update_bearer(old_spot, faulty)
    bearer_info = get_bearer(old_spot + 1)
    return bearer_info[0], bearer_info[1]

def get_all_handles():
    data = json_handler()
    token_dict = {}
    for i in data:
        id = i['Twitter Username']
        id = id.rstrip()
        token = i['TOKEN']
        category = i['Category / Basket']
        category = category.split(",")
        category = [x.strip(' ') for x in category]
        if id and id != 'unknow':
            token_dict.update({token: {"handle": id, "category": category}})
    return token_dict

def get_mention_count(handle, now, ago, client, spot, bearer): 
    length = len(get_all_bearers())
    fails = 0
    bigtime_fail = 0
    mention_count = -100
    while spot < length:
        try:
            mention_data = client.get_recent_tweets_count(f'@{handle} -is:retweet', end_time = now, start_time = ago)
            mention_count = mention_data[-1]['total_tweet_count']
            break
        except Exception as Argument:
            if "TooManyRequests" in str(repr(Argument)):
                print('too many req error')
                bearer_info = new_bearer(spot, 0)
                client = get_client(bearer_info[0])
                spot = bearer_info[1]
                print('switched')
            else:
                print(Argument)
                f = open(os.path.join(sys.path[0], "fooks_mentions.txt"), "a")
                f.write(f'other error: {Argument}\n')
                f.close()
                fails += 1
            if fails == 20:
                print('20x fail')
                f = open(os.path.join(sys.path[0], "fooks_mentions.txt"), "a")
                f.write(f'20x fail at {datetime.now()}\n')
                f.close()
                time.sleep(60)
                bigtime_fail += 1
                if bigtime_fail < 3:
                    time.sleep(60)
                if bigtime_fail == 3:
                    f = open(os.path.join(sys.path[0], "discarded_bearers_hashtags.txt"), "a")
                    f.write(f'Extremely sad fail at {datetime.now()}:\n{Argument}\n')
                    f.close()
                    webhook = Webhook.from_url("https://discord.com/api/webhooks/972978746275557376/Wg80pNqX2dG7fXY34ypmo0Rxifo0sVFlLMyDaQmfLKJwkwntTb95b-u8l7o9-agrWDzv", adapter=RequestsWebhookAdapter())
                    webhook.send(f"Fooked bearer:\n{bearer}")
                    bearer_info = new_bearer(spot, 1)
                    client = get_client(bearer_info[0])
                    spot = bearer_info[1]
                fails = 0

    return mention_count, client, spot

def get_data_all(now, ago, unix_stamp):
    new_data = {}
    timestamp_data = {}
    handle_dict = get_all_handles()
    bearer_info = get_bearer(0)
    client = get_client(bearer_info[0])
    spot = bearer_info[1]
    for token in handle_dict:
        handle = handle_dict[token]['handle']
        print(handle)
        category = handle_dict[token]['category']
        info = get_mention_count(handle, now, ago, client, spot, bearer_info[0])
        mention_count = info[0]
        client = info[1]
        spot = info[2]
        print(mention_count)
        new_data.update({token: {"mention_count": mention_count, "category": category}}) 
    timestamp_data.update({unix_stamp: new_data})
    timestamp_data_json = json.dumps(timestamp_data)
    return timestamp_data_json

def update_data_mentions(now, ago, unix_stamp):
    new_data = get_data_all(now, ago, unix_stamp)
    file_exists = os.path.exists(sys.path[0] + '/data_mentions_4h.json')
    if file_exists == False:
        with open(os.path.join(sys.path[0],"data_mentions_4h.json"), "w") as file:
            file.write(new_data)
    if file_exists == True:
        with open(os.path.join(sys.path[0],"data_mentions_4h.json"), "r+") as file:    
            data = json.load(file)                
            data.update(json.loads(new_data))
            file.seek(0)
            json.dump(data, file)
    return
