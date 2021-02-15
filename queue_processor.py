from pywinauto import Desktop
import time, requests, os, threading
import pyautogui
from pywinauto import timings

BASEURL = 'http://127.0.0.1:8000/'
PING_TIMEOUT = 45
PING_FREQUENCY = 45

QUEUE_LIMIT = 10
QUEUE_FREQUENCY = 5

q_processor = None
def exit_gracefully():
    if q_processor:
        q_processor.stop()
    exit(0)

class QProcessor():
    def __init__(self):
        self.thread = threading.Thread(target=self.process_queue)
        self.thread.setDaemon(True)
        self.stopping = False

    def start(self):
        self.thread.start()

    def process_queue(self):
        while not self.stopping:
            items = self.get_queue()

            if items:
                for item in items:
                    self.process(item['id'], item['component_id'], item['access_url'])

                time.sleep(0.1)
            else:
                time.sleep(QUEUE_FREQUENCY)

    def get_queue(self):
        data = []
        try:
            r = requests.get("{}{}".format(BASEURL, "job-queue/"), timeout=10)
            if r.status_code == 200:
                d = r.json()
                data = d['data_items'] if d['count'] > 0 else []
        except Exception as e:
            print(e)
            pass

        return data

    def process(self, id, component_id, access_url):
        try:
            r = requests.post("{}{}".format(BASEURL, "job-processor/"), data={
                'id' : id,
                'component_id' : component_id,
                'access_url' : access_url,
            }, timeout=45)
            print(r.json())
        except:
            try:
                windows = Desktop(backend="uia").windows()
                for win in windows:
                    try:
                        if ('OrCAD Capture CIS - Lite' in win.__str__()):
                            win.close()
                        else:
                            continue
                    except:
                        continue
            except:
                pass

    def stop(self):
        print('STOPPING TASK HANDLER.....')
        self.stopping = True
        while self.thread.is_alive():
            print('waiting for thread to finish.....')
            time.sleep(1)

if __name__ == '__main__':

    try: 

        q_processor = QProcessor()
        q_processor.start()

        ping_check = 0
        while True:
            time.sleep(10)
            print('.')
            ping_check += 1
            if ping_check >= PING_FREQUENCY:
                ping_check = 0

            
    except KeyboardInterrupt:
        print("exiting..using keyboard")
        exit_gracefully()
    except SystemExit as se:
        print("system existing..{}".format(se))
        exit_gracefully()
    except Exception as e:
        print("Error happen..{}".format(e))