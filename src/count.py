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


def pull_items():
    data = dict()
    to_extract = {
        "Category / Basket": "category",
        "HASHTAG": "hashtags",
        "Twitter Username": "handles"
    }
    data_tokens = dict()
    with open("data/sheet_tokens.txt", "r") as raw_sheet:
        for row in json.load(raw_sheet):
            token = row["TOKEN"]
            token_data = dict()
            for sheet_key, data_key in to_extract.items():
                token_data[data_key] = [token.strip() for token in row[sheet_key].split(',') if token]
            data_tokens[token] = token_data

    data_nfts = dict()
    with open("data/sheet_nfts.txt", "r") as raw_sheet:
        for row in json.load(raw_sheet):
            nft = row["NFT"]
            nft_data = dict()
            for sheet_key, data_key in to_extract.items():
                nft_data[data_key] = [nft.strip() for nft in row[sheet_key].split(',') if nft]
            data_nfts[nft] = nft_data
    data = {**data_tokens, **data_nfts}
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


def fetch_data(target, start_time, end_time, missing): 
    data_key = COUNT_QUERY_CONFIG[target]["data_key"]
    query_prefix = COUNT_QUERY_CONFIG[target]["query_prefix"]
    data = dict()
    logger.info(f"Fetching {target.name} data from {start_time} to {end_time}")
    if missing == 0:
        batch = pull_items()
    else:
        batch = missing
    for item, item_data in batch.items():
        if len(item_data[data_key]) == 0:
            logger.info(f"No query available for {item}, skipping for now")
            continue
        counts = dict()
        for query in item_data[data_key]:
            counts[query] = tweepy_count(f"{query_prefix}{query} -is:retweet", start_time, end_time)
        data[item] = { 
            "total": sum(counts.values()), 
            target.name: counts,
            "category": item_data["category"]
        }
        logger.info("Data retrieved for {}: {}".format(item, str(data[item])))
    logger.info("Done")
    
    return 
