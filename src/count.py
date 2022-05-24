from utils import state, get_or, log_to_discord, get_current_ts
from aggregate import aggregate

import time, json, os, sys
from datetime import datetime, timedelta
from enum import Enum

import tweepy
from loguru import logger


class CountQuery(str, Enum):
    hashtags = "hashtags"
    mentions = "mentions"

COUNT_QUERY_CONFIG = {
    CountQuery.hashtags: { "data_key": "hashtags", "query_prefix": "#" },
    CountQuery.mentions: { "data_key": "handles", "query_prefix": "@" }
}

TOKEN_COOLDOWN = 960 # seconds 


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


def tweepy_count(query, start_time, end_time):
    current_ts = get_current_ts()
    with open("credentials/twitter.json", "r") as file:
        tokens = json.load(file)["bearers"]
        token = next((t for t in tokens if get_or(0, f"ready_at_{t}") < current_ts), None)
        if token is None:
            logger.info("No token to use at the moment, aggregating and shutting down")
            aggregate()
            sys.exit(0)
        client = tweepy.Client(bearer_token=token)
        try:
            data = client.get_recent_tweets_count(query, start_time=start_time, end_time=end_time)
            return data[-1]["total_tweet_count"]
        except:
            logger.info(f"Cannot use {token} at the moment, fucking off for {TOKEN_COOLDOWN}s")
            state.set(f"ready_at_{token}", current_ts + TOKEN_COOLDOWN)
            return tweepy_count(query, start_time, end_time)



def fetch_data(target, start_time, end_time): 
    logger.info(f"Fetching {target.name} data from {start_time} to {end_time}")
    data_key = COUNT_QUERY_CONFIG[target]["data_key"]
    query_prefix = COUNT_QUERY_CONFIG[target]["query_prefix"]
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
    logger.info("Done")
    return data
