import glob
import logging
import logging.config
import os
import traceback

import pandas as pd

from ftp import delete_remote_files, download, list_remote_dir, upload_files
from utils import archive_past_days, delete_local_folder, mkdir_if_not_exists

dname = os.path.dirname(__file__)
os.chdir(dname)


logging.config.fileConfig("logging.conf", disable_existing_loggers=False)

logger = logging.getLogger(__name__)


def read_dat_files(dat_files):
    logger.debug("Reading .dat files...")
    df_list = []
    for dat_file in dat_files:
        df = pd.read_csv(
            dat_file,
            names=[
                "Datetime_UTC",
                "Anonymous1",
                "Anonymous2",
                "Tair_Avg",
                "RH_Avg",
                "WS",
                "WD",
                "WS_Max",
                "Rain_Tot",
                "Patm",
                "Batt_volt_Min",
                "Patm_corr",
            ],
            index_col="Datetime_UTC",
            parse_dates=True,
        )
        df_list.append(df)
    df_all = pd.concat(df_list)
    df_all = df_all.sort_index()
    logger.debug(f"Merged {len(dat_files)} files")
    return df_all


def save_to_daily_files(df, folder="daily", prefix=""):
    mkdir_if_not_exists(folder)
    days = [group[1] for group in df.groupby(df.index.date)]
    for day in days:
        fpath = f'{folder}/{prefix}{day.index[0].strftime("%Y%m%d")}.csv'
        day.to_csv(fpath, mode="a", header=not os.path.exists(fpath))
        logger.debug(f"Wrote {len(day)} rows in {fpath}")
    logger.info(f"Saved {len(days)} daily files")


def main():
    remote_dat_files = list_remote_dir(pattern="*.dat")
    download(remote_dat_files, local_folder="raw")
    local_dat_files = glob.glob("raw/*.dat")
    raw_data = read_dat_files(local_dat_files)
    save_to_daily_files(raw_data, folder="daily", prefix="koukouli1min_")
    daily_files = sorted(glob.glob("daily/*.csv"))
    upload_files(daily_files)
    archive_past_days(daily_files)
    delete_remote_files(remote_dat_files)
    delete_local_folder("raw")


if __name__ == "__main__":
    try:
        main()
    except:
        logger.error("uncaught exception: %s", traceback.format_exc())
