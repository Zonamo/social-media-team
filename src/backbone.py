from state import state
from utils import get_or, log_to_discord, get_current_ts

import time, json, os, sys
from datetime import datetime, time, timedelta
from enum import Enum

import tweepy
from loguru import logger


class CountTarget(str, Enum):
    hashtags = "hashtags"
    mentions = "mentions"

count_target_config = {
    CountTarget.hashtags: { "data_key": "hashtags", "query_prefix": "#" },
    CountTarget.mentions: { "data_key": "handles", "query_prefix": "@" }
}


def get_last_token_usage(bearer):
    return get_or(0, f"last_token_usage_{bearer}")


def set_last_token_usage(bearer, ts):
    state.set(f"last_token_usage_{bearer}", ts)



def get_coldest_token(target: CountTarget): 
    with open("credentials/twitter.json", "r") as file:
        tokens = json.load(file)[target]
        return min(tokens, key=lambda item: get_last_token_usage(item))


def pull_tokens():
    to_extract = {
        "Category / Basket": "category",
        "HASHTAG": "hashtags",
        "Twitter Username": "handles"
    }
    data = dict()
    with open("data/sheet.txt", "r") as raw_sheet:
        for row in json.load(raw_sheet):
            token = row["TOKEN"]
            token_data = dict()
            for sheet_key, data_key in to_extract.items():
                token_data[data_key] = [token.strip() for token in row[sheet_key].split(',') if token]
            data[token] = token_data
    return data


def tweepy_count(query, start_time, end_time, cooldown=60, max_attempts=20):
    logger.info(f"Querying Tweepy with {query}")
    bearer = get_coldest_token(CountTarget.hashtags)
    client = tweepy.Client(bearer_token=bearer)
    for attempt in range(max_attempts):
        last_attempt = attempt + 1 == max_attempts
        try:
            set_last_token_usage(bearer, get_current_ts())
            data = client.get_recent_tweets_count(query, start_time=start_time, end_time=end_time)
            return data[-1]["total_tweet_count"]
        except Exception as e:
            if not last_attempt:
                logger.error(f"Failed with {e}, retrying after {cooldown}s...")
                time.sleep(cooldown)
            else:
                log_to_discord(f"Fucked up token - {bearer}")
                logger.info("Token {bearer} is fucked up, invalidating")
                set_last_token_usage(bearer, 10**18)
                pass


def retrieve_data(target, start_time, end_time, ts): 
    data_key = count_target_config[target]["data_key"]
    query_prefix = count_target_config[target]["query_prefix"]
    data = dict()
    for token, token_data in pull_tokens().items():
        counts = dict()
        for query in token_data[data_key]:
            counts[query] = tweepy_count(f"{query_prefix}{query} -is:retweet", start_time, end_time)
        data[token] = { 
            "total": sum(counts.values()), 
            target.name: counts,
            "category": token_data["category"]
        }
        logger.info("Data retrieved for {}: {}".format(token, str(data[token])))
    return { ts: data }


def update_data(target, start_time, end_time, ts): 
    logger.info(f"Updating {target} data...")
    with open(f"data/data_{target}_4h.json", "w+") as file:
        try:
            data = json.load(file)
        except:
            data = dict()
        data.update(retrieve_data(target, start_time, end_time, ts))
        json.dump(data, file)
        logger.info("Done")
