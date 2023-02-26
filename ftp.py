import fnmatch
import glob
import logging
import os
from ftplib import FTP, error_perm

from utils import mkdir_if_not_exists

FTP_IP = ""
FTP_USER = ""
FTP_PASSWORD = ""
FTP_DIR = "/dataloggers/koukouli"

logger = logging.getLogger(__name__)


def list_remote_dir(pattern="*.dat"):
    with FTP(FTP_IP, FTP_USER, FTP_PASSWORD) as ftp_session:
        ftp_session.cwd(FTP_DIR)
        ftp_dir_list = ftp_session.nlst()
    selected_files = fnmatch.filter(ftp_dir_list, pattern)
    logger.debug(f"Found {len(selected_files)} {pattern} files in FTP")
    return selected_files


def download(remote_files, local_folder="raw"):
    mkdir_if_not_exists(local_folder)
    local_dat_files = glob.glob("raw/*.dat")
    local_dat_file_basenames = [s[4:] for s in local_dat_files]
    remaining = set(remote_files).difference(local_dat_file_basenames)
    logger.debug(
        f"{len(remaining)} files not found locally. Downloading them from FTP..."
    )
    with FTP(FTP_IP, FTP_USER, FTP_PASSWORD) as ftp_session:
        ftp_session.cwd(FTP_DIR)
        for count, fname in enumerate(remaining):
            with open(f"{local_folder}/{fname}", "wb") as f:
                ftp_session.retrbinary("RETR " + fname, f.write)
            print(
                f"Downloaded {count} of {len(remaining)} files",
                sep="",
                end="\r",
                flush=True,
            )
    logger.info(f"Downloaded {len(remaining)} files from FTP")


def upload_file(ftp_session, local_path, remote_path):
    with open(local_path, "rb") as f:
        ftp_session.storbinary(f"STOR {remote_path}", f)
    logger.info(f"Uploaded {local_path} to {remote_path}")


def mkdir_and_enter(ftp_session, dir_name):
    if dir_name not in ftp_session.nlst():
        ftp_session.mkd(dir_name)
        logger.debug(f"Created FTP directory {dir_name}")
    ftp_session.cwd(dir_name)


def make_dirs(ftp_session, folder_path):
    for f in folder_path.split("/"):
        mkdir_and_enter(ftp_session, f)


def upload_files(local_files):
    with FTP(FTP_IP, FTP_USER, FTP_PASSWORD) as ftp_session:
        ftp_session.cwd(FTP_DIR)
        for local_file in local_files:
            base_name = os.path.basename(local_file)
            year = base_name.split("_")[1][:4]
            remote_path = f"{year}/{base_name}"
            try:
                upload_file(ftp_session, local_file, remote_path)
            except error_perm as e:
                if "55" in str(e):
                    make_dirs(ftp_session, os.path.dirname(remote_path))
                    ftp_session.cwd(FTP_DIR)
                    upload_file(ftp_session, local_file, remote_path)


def delete_remote_files(remote_files):
    logger.debug("Deleting FTP files...")
    with FTP(FTP_IP, FTP_USER, FTP_PASSWORD) as ftp_session:
        ftp_session.cwd(FTP_DIR)
        for count, remote_file in enumerate(remote_files):
            ftp_session.delete(remote_file)
            print(
                f"Deleted {count} of {len(remote_files)} files",
                sep="",
                end="\r",
                flush=True,
            )
    logger.info(f"Deleted {len(remote_files)} files from FTP")
