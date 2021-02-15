from datetime import datetime
from pywinauto.application import Application
from pywinauto import timings
import os, logging, re, shutil, subprocess, sys, zipfile, pyautogui

logger = logging.getLogger("django.error")
logger_info = logging.getLogger("django.info")


class BatchExtractor(object):
    """
    Receives a zipped file location and extracts all the contents of the file
    Uses allegro application to convert edf files to olb
    """

    def __init__(self, zip_location):
        self.zip_location = zip_location

    def extract_files(self):
        # This method will extract the zipped file in the specified location
        # Returns True if extracted successfully
        try:
            zip_ref = zipfile.ZipFile(self.zip_location, "r")
            self.extracted_folder = self.zip_location[:-4] + "_extracted"
            # Remove directory if it is already existed to prevent overwrite errors
            if os.path.exists(self.extracted_folder):
                shutil.rmtree(self.extracted_folder)
            zip_ref.extractall(self.extracted_folder)
            zip_ref.close()
            return True
        except:
            return False

    def process_files(self):
        self.execute_batch()
        self.collect_files()
        self.move_files(True)

        with open(self.processed_zip, "rb") as f:
            return f.read()

    def collect_files(self):
        processed_files = os.listdir(self.extracted_folder)
        logger_info.info(processed_files)
        match_string = ".*(\.dra|\.edf|\.html|\.pad|\.psm|\.ssm|\.CFG|\.olb)"
        self.final_files = [
            file for file in processed_files if re.match(match_string, file)
        ]

        self.processed_zip = self.zip_location[:-4] + "_processed.zip"
        self.processed_zip_full = (
            "./" + self.extracted_folder + "/" + self.processed_zip
        )
        new_zip = zipfile.ZipFile(self.processed_zip_full, "w")
        for file in self.final_files:
            shutil.copy("./" + self.extracted_folder + "/" + file, "./" + file)
            new_zip.write(file)
            os.remove("./" + file)
        new_zip.close()

    def move_files(self, delete_folder):
        shutil.move(self.processed_zip_full, "./" + self.processed_zip)
        if delete_folder:
            shutil.rmtree("./" + self.extracted_folder, True)

    def execute_batch(self):
        pyautogui.PAUSE = 1
        timings.after_clickinput_wait = 1

        directory = os.path.join(os.path.abspath(sys.path[0]))
        process = subprocess.Popen("open.bat", cwd=directory + "\\", shell=True)

        poll = process.poll()
        start_time = datetime.now()
        time_multiplier = 1
        while poll == None:
            poll = process.poll()
            app = Application(backend="uia").connect(
                path=r"C:\Cadence\SPB_16.6\tools\capture\Capture.exe"
            )
            app.Dialog.wait("ready")
            app.Dialog.maximize()
            poll = process.poll()
            # Clicks may very depending on screen resolution
            pyautogui.click(10, 30)
            pyautogui.click(60, 350)
            pyautogui.click(860, 400)
            pyautogui.click(860, 448)
            pyautogui.hotkey("ctrl", "a")
            # This is for testing only
            pyautogui.typewrite(
                r"{}\{}.edf".format(
                    self.extracted_folder,
                    self.zip_location.split("\\")[-1].split(".")[0],
                )
            )
            pyautogui.click(860, 535)
            pyautogui.hotkey("ctrl", "a")
            # Modify this to a more dynamic url. This is for testing only
            pyautogui.typewrite(r"{}\EDI2CAP.CFG".format(self.extracted_folder))
            pyautogui.click(920, 660)
            current_time = datetime.now()
            time_delta = current_time - start_time
            if time_delta.seconds > 120 * time_multiplier:
                pyautogui.hotkey("alt", "f4")
                # this R before the ALT + F4 combi is to choose shutdown instead sign off
                pyautogui.hotkey("r")
                time_multiplier = time_multiplier + 1
                logger.error("{}: conversion timeout".format(self.zip_location))
        process.wait()
