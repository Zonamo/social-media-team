from utils import state, get_or, get_current_ts, log_to_discord
from count import CountQuery, fetch_data
from aggregate import aggregate

import time, os, sys, json
from datetime import date, datetime, timedelta

import gspread
from loguru import logger


MAX_LOOKBACK = timedelta(days=7) # twitter api limitation


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


def fetch():
    today, now = date.today(), datetime.utcnow()

    for target in CountQuery:
        data = dict()
        try:
            data = json.load(open(f"data/{target.name}.json", "r"))
        except: pass

        missing_h4 = []
        for days_back in range(8):
            day = today - timedelta(days=days_back)
            for h4_start in reversed(range(0, 24, 4)):
                start_time = datetime.combine(day, datetime.min.time()) + timedelta(hours=h4_start)
                end_time = start_time + timedelta(hours=4)
                if end_time > now or now - start_time > MAX_LOOKBACK: 
                    continue
                key = str(int(datetime.timestamp(start_time)))
                if not key in data: 
                    missing_h4.append((key, target, start_time, end_time))

        logger.info(f"A total of {len(missing_h4)} H4 {target.name} block(s) missing")

        for (key, target, start_time, end_time) in missing_h4:
            data[key] = fetch_data(target, start_time, end_time)
            with open(f"data/{target.name}.json", "w+") as file:
                json.dump(data, file, sort_keys=True)
 

logger.info(f"Cronjob started")
load_spreadsheet()
fetch()
aggregate()
logger.info("Cronjob finished")

