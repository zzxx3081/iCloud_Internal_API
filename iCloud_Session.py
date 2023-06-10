import os, json, datetime
from termcolor import colored

class Session:
    # Session Init (Format : dict)
    def __init__(self):
        self.SessionJson = {}

    # return Session value
    def getSesssion(self):
        return self.SessionJson
    

    # Save Session Data
    def saveSession(self, filePath):
        fileName = datetime.datetime.now().strftime("%y%m%d_%H%M%S_Session.json")
        fullPath = os.path.join(filePath, fileName)

        with open(fullPath, 'w', encoding='UTF-8') as outSessionFile:
            json.dump(self.SessionJson, outSessionFile, indent=4, ensure_ascii=False)

        print(colored(f"[Success] Save the Session File : {fullPath}" + "\n", 'blue'))

    # Read Session Data
    def readSession(self, filePath):
        try:
            with open(filePath, 'r', encoding='UTF-8') as InSessionFile:
                self.SessionJson = json.load(InSessionFile)

            print(colored(f"\n[Success] Read the Session File : {filePath}" + "\n", 'blue'))
            return self.SessionJson
        except Exception as e:
            print("[Fail] Invalid Session path", e)