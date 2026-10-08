import logging
import os
import shutil

import pandas as pd

logger = logging.getLogger(__name__)

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def mkdir_if_not_exists(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        logger.info(f"Created local directory: {dir_path}")


def archive_past_days(local_files):
    if len(local_files) > 1:
        for local_file in local_files[:-1]:
            base_name = os.path.basename(local_file)
            year = base_name.split("_")[1][:4]
            dest_folder = f"daily/archive/{year}"
            dest_path = f"{dest_folder}/{base_name}"
            mkdir_if_not_exists(dest_folder)
            os.rename(local_file, dest_path)
            logger.info(f"Renamed local file {local_file} to {dest_path}")


def delete_local_folder(dirname):
    shutil.rmtree(dirname)
    logger.info(f"Deleted local folder: {dirname}")


def parse_datetime_index(df, source):
    """Converts the index to timestamps. Drops rows that aren't timestamps, e.g. junk written over an upload."""
    parsed = pd.to_datetime(df.index, format=DATETIME_FORMAT, errors="coerce")
    invalid = parsed.isna()
    if invalid.any():
        logger.warning(f"Dropped {invalid.sum()} rows with invalid timestamps from {source}")
    df.index = parsed
    return df[~invalid]


def concat_sorted(df_list):
    if len(df_list) > 0:
        df_all = pd.concat(df_list).sort_index()
    else:
        df_all = pd.DataFrame(index=pd.DatetimeIndex([], name="Datetime_UTC"))
    return df_all
