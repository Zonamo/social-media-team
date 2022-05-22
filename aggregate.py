import os
import json
import sys

def json_handler(file):
  with open(os.path.join(sys.path[0], file), 'r') as file:
      string = file.read()
      data = json.loads(string)    
  return data

def get_update_count():
    with open(os.path.join(sys.path[0], 'update_count.txt'), 'r') as file:
        count = int(file.read())
    return count

def get_unix_stamp():
    with open(os.path.join(sys.path[0], 'unix_stamp.txt'), 'r') as file:
        string = file.read()
        unix_stamp = int(json.loads(string))
    return unix_stamp

def general_aggregate(period, last_unix_stamp, n_times, get_from, push_to):
    data_hashtags = json_handler(f'data_hashtags_{get_from}.json')
    data_mentions = json_handler(f'data_mentions_{get_from}.json')
    new_dict_hashtags = data_hashtags[f'{last_unix_stamp}']
    new_dict_mentions = data_mentions[f'{last_unix_stamp}']
    unix_stamp = last_unix_stamp
    i = 1
    while i < n_times:
        unix_stamp = int(unix_stamp) - (period * 60)
        unix_stamp = format(unix_stamp, '.0f')
        earlier_batch_hashtags = data_hashtags[f'{unix_stamp}']
        earlier_batch_mentions = data_mentions[f'{unix_stamp}']
        for token in list(new_dict_hashtags):
            try:
                earlier_hashtag_data_hashtags = earlier_batch_hashtags[token]['hashtags']
                earlier_hashtag_data_total = earlier_batch_hashtags[token]['total']
                added_hashtag_data_hashtags = new_dict_hashtags[token]['hashtags']
                added_hashtag_data_total = new_dict_hashtags[token]['total']
                new_total = earlier_hashtag_data_total + added_hashtag_data_total
                category = new_dict_hashtags[token]['category']
                for hashtag in list(added_hashtag_data_hashtags):
                    try:
                        added = earlier_hashtag_data_hashtags[hashtag] + added_hashtag_data_hashtags[hashtag]
                        added_hashtag_data_hashtags.update({hashtag: added})
                    except Exception as e:
                        hashtag = e.args[0]
                        print(f'hash aggr error hash: {hashtag}')
                        new_dict_hashtags[token]['hashtags'].pop(hashtag, None)
                        continue
                new_dict_hashtags.update({token: {'total': new_total, 'hashtags': added_hashtag_data_hashtags, 'category': category}})    
            except Exception as e:
                token = e.args[0]
                print(f'hash aggr error token: {token}')
                new_dict_hashtags.pop(token, None)
                continue

        for token in list(new_dict_mentions):
            try:
                earlier_mention_data = earlier_batch_mentions[token]['mention_count']
                added_mention_data = new_dict_mentions[token]['mention_count']
                added = earlier_mention_data + added_mention_data
                category = new_dict_mentions[token]['category']
                new_dict_mentions.update({token: {'mention_count': added, 'category': category}})
            except Exception as e:
                token = e.args[0]
                print(f'mention aggr error token: {token}')
                new_dict_mentions.pop(token, None)
        i += 1

    daily_dict_hashtags = json.dumps({last_unix_stamp: new_dict_hashtags})
    daily_dict_mentions = json.dumps({last_unix_stamp: new_dict_mentions})
    file_exists = os.path.exists(sys.path[0] + f'/data_hashtags_{push_to}.json')
    if file_exists == False:
        with open(os.path.join(sys.path[0],f"data_hashtags_{push_to}.json"), "w") as file:
            file.write(daily_dict_hashtags)
        with open(os.path.join(sys.path[0],f"data_mentions_{push_to}.json"), "w") as file:
            file.write(daily_dict_mentions)
    if file_exists == True:
        with open(os.path.join(sys.path[0],f"data_hashtags_{push_to}.json"), "r+") as file:    
            data = json.load(file)                
            data.update(json.loads(daily_dict_hashtags))
            file.seek(0)
            json.dump(data, file)
        with open(os.path.join(sys.path[0],f"data_mentions_{push_to}.json"), "r+") as file:    
            data = json.load(file)                
            data.update(json.loads(daily_dict_mentions))
            file.seek(0)
            json.dump(data, file)
    return

def aggregate(period):
    nth_update = get_update_count()
    last_unix_stamp = get_unix_stamp()
    print(f'nth update: {nth_update}')
    #daily - uses 4h data
    if nth_update % 6 == 0:     
        print(f'aggregating for day at {last_unix_stamp}')  
        general_aggregate(period, last_unix_stamp, 6, '4h', 'day')
    #weekly - uses daily
    if nth_update % 42 == 0:
        print(f'aggregating for week at {last_unix_stamp}')
        general_aggregate((period * 6), last_unix_stamp, 7, 'day', 'week')
    #monthly - uses weekly data
    if nth_update % 168 == 0:
        print(f'aggregating for month at {last_unix_stamp}')
        general_aggregate((period * 42), last_unix_stamp, 4, 'week', 'month')
    return 
