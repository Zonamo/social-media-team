import subprocess
import sys
from datetime import datetime
import time
import os
import json

from state import state
import gspread

# from utils import log_to_discord
from loguru import logger


def load_spreadsheet(path="data/sheet.txt", max_attempts=4, cooldown=60):
    logger.info('Loading spreadsheet...')
    for attempt in range(max_attempts):
        last_attempt = attempt + 1 == max_attempts
        try:
            account = gspread.service_account(filename=os.path.join(sys.path[0], "../credentials/google.json"))
            sheet = account.open_by_key("1w4wNzx2Yk2I3knQw-VHzFll6QQpAK9aOGi90Osuguks")
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
                # log_to_discord(f"Failed loading spreadsheet {max_attempts} times - {e}")
                pass


def init():
    if not state.get("launched_before"):
        logger.info('Initializing state on first launch...')
        state.set("launched_before", True)
        state.set("update_count", 0)
    load_spreadsheet()



