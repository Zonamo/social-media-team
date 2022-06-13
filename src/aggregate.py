import time, os, sys, json
from datetime import date, datetime, timedelta

from loguru import logger


def aggregate():
    for target in ["hashtags", "mentions"]:
        logger.info(f"Aggregating {target} data")
        data = dict()
        try:
            data = json.load(open(os.path.join(sys.path[0],f"../data/{target}.json"), "r"))
        except: pass
        stamps = list(data.keys())
        for timeframe, bucket in [("4h", 1), ("day", 6), ("week", 42), ("month", 1260)]:
            aggregated_data = dict()
            for idx in range(0, len(stamps), bucket):
                aggregated = data[stamps[idx]]
                bucket_end = min(len(stamps), idx + bucket)
                for other_idx in range(idx + 1, bucket_end):
                    for token in aggregated.keys():
                        #skips if token got deleted from sheet
                        try:
                            aggregated[token]["total"] += data[stamps[other_idx]][token]["total"]
                            for query in aggregated[token][target].keys():
                                aggregated[token][target][query] += data[stamps[other_idx]][token][target][query]
                        except:
                            continue
                aggregated_data[stamps[bucket_end - 1]] = aggregated
            with open(os.path.join(sys.path[0], f"../data/data_{target}_{timeframe}.json"), "w+") as file:
                json.dump(aggregated_data, file, sort_keys=True)    
        logger.info("Done")
