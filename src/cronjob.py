from datetime import datetime, timedelta
import time
import sys

from state import state
from utils import get_current_ts

from aggregate import aggregate

from loguru import logger

from utils import get_or
from backbone import CountTarget, update_data

from init import init



from utils import log_to_discord


PERIOD = 240 # minutes
 
ts = get_current_ts()
logger.info(f"Running cronjob at {ts}...")

last_run_ts = get_or(0, "last_run_ts")

if ts - last_run_ts < PERIOD * 60:
    logger.info(f"Specified period not elapsed since last run at {last_run_ts}, shutting down")
    sys.exit(0)

start_time = datetime.utcfromtimestamp(ts) - timedelta(minutes=PERIOD) 
end_time = (datetime.utcfromtimestamp(ts) - timedelta(seconds=10)).replace(microsecond=0)

logger.info(f"Request period: from {start_time} to {end_time}")

init()

for target in CountTarget:
    update_data(target, start_time, end_time, ts)

aggregate(PERIOD)

state.set("last_run_ts", ts)
state.set("update_count", get_or(0, "update_count") + 1)
logger.info("Cronjob finished")
