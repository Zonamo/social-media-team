from state import state
from utils import log_to_discord

import time, os, json, sys
from datetime import datetime

import gspread
from loguru import logger


def load_spreadsheet(path="data/sheet.txt", max_attempts=4, cooldown=60):
    logger.info('Loading spreadsheet...')
    spreadsheet_key = json.load(open('credentials/misc.json', 'r'))["spreadsheet_key"]
    for attempt in range(max_attempts):
        last_attempt = attempt + 1 == max_attempts
        try:
            account = gspread.service_account(filename="credentials/google.json")
            sheet = account.open_by_key(spreadsheet_key)
            records = sheet.sheet1.get_all_records()
            with open(path, "w") as sheet_txt:
                sheet_txt.write(json.dumps(records))
            logger.info(f"Done, saved to: {path}")
            break
        except Exception as e:
            logger.error(f"Failed loading spreadsheet - {e}")
            if not last_attempt:
                time.sleep(cooldown)
            else:
                log_to_discord(f"Failed loading spreadsheet {max_attempts} times - {e}")


def init():
    if not state.get("launched_before"):
        logger.info('Initializing state on first launch...')
        state.set("launched_before", True)
        state.set("update_count", 0)
    load_spreadsheet()
