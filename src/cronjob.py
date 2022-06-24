from utils import state, get_or, get_current_ts, log_to_discord
from count import CountQuery, fetch_data, pull_items
from aggregate import aggregate

import time, os, sys, json
from datetime import date, datetime, timedelta

import gspread
from loguru import logger


MAX_LOOKBACK = timedelta(days=7) # twitter api limitation


def load_spreadsheet(max_attempts=4, cooldown=60):
    path_token = "../data/sheet_tokens.txt"
    path_nft = "../data/sheet_nfts.txt"
    path_bearer = "../credentials/twitter.json"
    logger.info('Loading spreadsheet...')
    spreadsheet_key = json.load(open(os.path.join(sys.path[0], '../credentials/misc.json'), 'r'))["spreadsheet_key"]
    for attempt in range(max_attempts):
        last_attempt = attempt + 1 == max_attempts
        try:
            account = gspread.service_account(filename=(os.path.join(sys.path[0], "../credentials/google.json")))
            sheet = account.open_by_key(spreadsheet_key)
            token_records = sheet.sheet1.get_all_records()
            nft_records = sheet.worksheet("NFT Baskets").get_all_records()
            bearer_records = sheet.worksheet("Bearer Tokens").get_all_records()
            bearer_list = []
            for i in bearer_records:
                bearer_list.append(i['F'])
            bearer_data = { "bearers": bearer_list }
            with open(os.path.join(sys.path[0], path_token), "w") as sheet_txt:
                sheet_txt.write(json.dumps(token_records))
            logger.info(f"Token sheet done, saved to: {path_token}")
            with open(os.path.join(sys.path[0], path_nft), "w") as sheet_txt:
                sheet_txt.write(json.dumps(nft_records))
            logger.info(f"Nft sheet done, saved to: {path_nft}")
            with open(os.path.join(sys.path[0], path_bearer), "w") as sheet_txt:
                sheet_txt.write(json.dumps(bearer_data))
            logger.info(f"Bearer sheet done, saved to: {path_bearer}")
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
            data = json.load(open(os.path.join(sys.path[0], f"../data/{target.name}.json"), "r"))
        except: pass

        missing_h4 = []
        rest_h4 = []
        for days_back in range(8):
            day = today - timedelta(days=days_back)
            for h4_start in reversed(range(0, 24, 4)):
                start_time = datetime.combine(day, datetime.min.time()) + timedelta(hours=h4_start)
                end_time = start_time + timedelta(hours=4)
                if end_time > now or now - start_time > MAX_LOOKBACK: 
                    continue
                key = str(int(datetime.timestamp(end_time)))
                if not key in data: 
                    missing_h4.append((key, target, start_time, end_time))
                if key in data:
                    rest_h4.append((key, target, start_time, end_time))

        logger.info(f"A total of {len(missing_h4)} H4 {target.name} block(s) missing")

        if len(rest_h4) != 0:
            last_updated_key = rest_h4[0][0]
            last_data_set = data[last_updated_key]
            missing_items = dict()
            for key in pull_items():
                if key not in last_data_set:
                    missing_items[key] = pull_items()[key]

            logger.info(f"A total of {len(missing_items)} new items")

            if len(missing_items) != 0:
                for (key,target,start_time, end_time) in reversed(rest_h4):
                    logger.info(f"Missing items fetch, Key = {key}")
                    data[key].update(fetch_data(target, start_time, end_time, missing_items))
                    with open(os.path.join(sys.path[0], f"../data/{target.name}.json"), "w+") as file:
                        json.dump(data, file, sort_keys=True)
                    logger.info(f"Missing items appended to dataset")

        for (key, target, start_time, end_time) in reversed(missing_h4):
            logger.info(f"Key fetch = {key}")
            data[key] = fetch_data(target, start_time, end_time, 0)
            with open(os.path.join(sys.path[0], f"../data/{target.name}.json"), "w+") as file:
                json.dump(data, file, sort_keys=True)
 

logger.info(f"Cronjob started")
load_spreadsheet()
fetch()
aggregate()
logger.info("Cronjob finished")

