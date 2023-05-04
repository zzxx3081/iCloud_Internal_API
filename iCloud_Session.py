import os, json, datetime


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

        print(f"[Success] Save the Session File : {fullPath}" + "\n")

    # Read Session Data
    def readSession(self, filePath):
        with open(filePath, 'r', encoding='UTF-8') as InSessionFile:
            self.SessionJson = json.load(InSessionFile)

        print(f"[Success] Read the Session File : {filePath}" + "\n")
        return self.SessionJson
        
        