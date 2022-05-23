from state import state

import time

import tweepy
from discord import Webhook, RequestsWebhookAdapter
from loguru import logger


def get_current_ts():
    return int(time.time()) 


def log_to_discord(message, cooldown=60):
    hook_url = json.load("credentials/misc.json")["discord_hook_url"]
    logger.info(f"Critical error - {message} - relaying to Discord...")
    try:
        webhook = Webhook.from_url(hook_url, adapter=RequestsWebhookAdapter())
        webhook.send(message)
        logger.info("Done")
    except Exception as e:
        logger.error(f"Failed with {e}, retrying after {cooldown}s...")
        time.sleep(cooldown)
        log_to_discord(message)  


def get_or(default, key):
    value = state.get(key)
    if value is not None:
        return value
    state.set(key, default)
    return default
    