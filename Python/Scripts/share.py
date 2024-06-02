import pandas as pd
import os
import shutil
import time
import datetime
import logging
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class FileMover(FileSystemEventHandler):
    def __init__(self, watch_directory, destination_directory, company_lookup_path):
        self.watch_directory = watch_directory
        self.destination_directory = destination_directory
        self.company_lookup_path = company_lookup_path
        self.load_company_data()
        self.max_retries = 10  # Increase max retries to 10
        self.retry_wait_time = 4  # Wait 5 seconds between retries
        self.initial_delay = 20  # Initial delay of 10 seconds before processing

    def load_company_data(self):
        try:
            self.company_df = pd.read_excel(self.company_lookup_path)
            logging.info("Company lookup data successfully loaded.")
        except Exception as e:
            logging.error(f"Failed to load company lookup data: {e}")
            raise

    def on_created(self, event):
        if (
            event.is_directory
            or not event.src_path.endswith(".xlsx")
            or event.src_path.endswith((".tmp", ".temp"))
        ):
            return
        logging.info(f"New file detected: {event.src_path}")
        time.sleep(self.initial_delay)  # Add initial delay
        self.process_file(event.src_path)

    def process_file(self, file_path):
        try:
            if not self.wait_for_file_to_be_ready(file_path):
                logging.error(
                    f"File {file_path} could not be processed after maximum retries."
                )
                return
            df = pd.read_excel(file_path)
            company_number = self.extract_company_number(df)
            if company_number is None:
                logging.warning("Customer account number not found.")
                company_number = "Unknown"
            abbreviation = self.lookup_company_abbreviation(company_number)
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            new_file_name = (
                f"{company_number}-{abbreviation}_{date_str}.xlsx"
                if company_number != "Unknown"
                else f"{date_str}.xlsx"
            )
            new_file_path = os.path.join(self.destination_directory, new_file_name)
            shutil.move(file_path, new_file_path)
            logging.info(f"Moved and renamed file to {new_file_path}")
            self.cleanup_tmp_files()
        except Exception as e:
            logging.error(f"Error processing file {file_path}: {e}")

    def wait_for_file_to_be_ready(self, file_path):
        retries = 0
        while retries < self.max_retries:
            try:
                with open(file_path, "rb") as f:
                    return True
            except IOError:
                retries += 1
                logging.warning(
                    f"File not ready for processing, retrying ({retries}/{self.max_retries}): {file_path}"
                )
                time.sleep(self.retry_wait_time)
        return False

    def extract_company_number(self, df):
        logging.info("Attempting to extract company number from the DataFrame.")
        for index, row in df.iterrows():
            for item in row:
                logging.debug(f"Checking cell value: {item}")
                if isinstance(item, str) and re.match(r"C0\d{4}", item):
                    logging.info(f"Found company number: {item}")
                    return item
        logging.error("Customer account number not found in the DataFrame.")
        return None

    def lookup_company_abbreviation(self, company_number):
        result = self.company_df[self.company_df["Company No."] == company_number][
            "Abbreviation"
        ]
        if not result.empty:
            abbreviation = result.iloc[0]
            logging.info(f"Found company abbreviation: {abbreviation}")
            return abbreviation
        else:
            logging.error(
                f"Company abbreviation for account {company_number} not found."
            )
            return "Unknown"

    def cleanup_tmp_files(self):
        for file in os.listdir(self.watch_directory):
            if file.endswith(".tmp"):
                os.remove(os.path.join(self.watch_directory, file))
                logging.info(f"Deleted temporary file: {file}")


def start_monitoring(watch_directory, destination_directory, company_lookup_path):
    event_handler = FileMover(
        watch_directory, destination_directory, company_lookup_path
    )
    observer = Observer()
    observer.schedule(event_handler, watch_directory, recursive=False)
    observer.start()
    logging.info(f"Started monitoring {watch_directory}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


# Parameters
watch_directory = (
    "\\\\LNCSynoFS01\\FileShare\\SALES-MARKETING\\Price Update Emails (Acctg)\\AX Docs"
)
destination_directory = (
    "C:\\Users\\mrice\\OneDrive - Kalas Manufacturing Inc\\1 AX_Data Source\\AX_Sync"
)
company_lookup_path = "C:\\Users\\mrice\\OneDrive - Kalas Manufacturing Inc\\1 AX_Data Source\\Tables\\Company abbreviations.xlsx"

# Uncomment to start
start_monitoring(watch_directory, destination_directory, company_lookup_path)
