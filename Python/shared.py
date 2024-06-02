import pandas as pd
import os
import shutil
import time
import datetime  # Ctrl + Alt + R to pause, Ctrl + Shift + R to resume
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
        self.initial_delay = 20  # Initial delay of 20 seconds before processing
        self.running = True  # Control flag for pausing/stopping

    def load_company_data(self):
        try:
            self.company_df = pd.read_excel(
                self.company_lookup_path, usecols=["Customer No.", "Abbrev"]
            )
            logging.info("Company lookup data successfully loaded.")
        except Exception as e:
            logging.error(f"Failed to load company lookup data: {e}")
            raise

    def on_created(self, event):
        if not self.running:
            return
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
            custom_name = self.check_for_custom_name(df)

            if custom_name:
                new_file_name = (
                    f"{company_number}-{abbreviation}_{custom_name}_{date_str}.xlsx"
                )
            else:
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
        result = self.company_df[self.company_df["Customer No."] == company_number][
            "Abbrev"
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

    def check_for_custom_name(self, df):
        try:
            custom_name = df.at[2, df.columns[0]]  # Accessing cell A3
            if isinstance(custom_name, str) and custom_name.startswith("**"):
                return custom_name[2:].strip()
            return None
        except Exception as e:
            logging.error(f"Error checking for custom name in cell A3: {e}")
            return None

    def cleanup_tmp_files(self):
        for file in os.listdir(self.watch_directory):
            if file.endswith(".tmp"):
                os.remove(os.path.join(self.watch_directory, file))
                logging.info(f"Deleted temporary file: {file}")

    def process_existing_files(self):
        for file_name in os.listdir(self.watch_directory):
            if file_name.endswith(".xlsx") and not file_name.endswith(
                (".tmp", ".temp")
            ):
                self.process_file(os.path.join(self.watch_directory, file_name))

    def stop(self):
        self.running = False
        logging.info("File mover has been paused.")

    def start(self):
        self.running = True
        logging.info("File mover has been resumed.")


def start_monitoring(watch_directory, destination_directory, company_lookup_path):
    event_handler = FileMover(
        watch_directory, destination_directory, company_lookup_path
    )
    observer = Observer()
    observer.schedule(event_handler, watch_directory, recursive=False)
    observer.start()
    logging.info(f"Started monitoring {watch_directory}")

    # Process existing files upon start
    event_handler.process_existing_files()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

    return event_handler


# Parameters
watch_directory = (
    "\\\\LNCSynoFS01\\FileShare\\SALES-MARKETING\\Price Update Emails (Acctg)\\AX Docs"
)
destination_directory = (
    "C:\\Users\\mrice\\OneDrive - Kalas Manufacturing Inc\\1 AX_Data Source\\AX_Sync"
)
company_lookup_path = "C:\\Users\\mrice\\OneDrive - Kalas Manufacturing Inc\\1 AX_Data Source\\Tables\\Abbreviated_Names.xlsx"

# Start monitoring
file_mover_handler = start_monitoring(
    watch_directory, destination_directory, company_lookup_path
)

# Keyboard shortcuts to control the script
import keyboard  # Requires installing `keyboard` library

keyboard.add_hotkey("ctrl+alt+r", lambda: file_mover_handler.stop())
keyboard.add_hotkey("ctrl+shift+r", lambda: file_mover_handler.start())

# Example URL trigger setup (requires additional web server setup)
from flask import Flask, request

app = Flask(__name__)


@app.route("/control", methods=["POST"])
def control():
    action = request.form.get("action")
    if action == "stop":
        file_mover_handler.stop()
        return "File mover stopped."
    elif action == "start":
        file_mover_handler.start()
        return "File mover started."
    elif action == "run":
        file_mover_handler.process_existing_files()
        return "Existing files processed."
    else:
        return "Invalid action."


if __name__ == "__main__":
    app.run(port=5000)
