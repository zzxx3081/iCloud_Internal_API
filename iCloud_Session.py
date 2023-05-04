import os, json, datetime


class Session:
    def __init__(self):
        self.SessionJson = {}

    # 세션을 변수화해서 내보내기 (다른 서비스의 인증 수단으로 활용하기 위함)
    def getSesssion(self):
        return self.SessionJson

    # 세션을 Json 파일로 저장 (경로, 이름)
    def saveSession(self, filePath):
        fileName = datetime.datetime.now().strftime("%y%m%d_%H%M%S_Session.json")
        fullPath = os.path.join(filePath, fileName)

        with open(fullPath, 'w', encoding='UTF-8') as outSessionFile:
            json.dump(self.SessionJson, outSessionFile, indent=4, ensure_ascii=False)

        print(f"[Success] Save the Session File : {fullPath}" + "\n")

    # 세션 Json 파일을 읽고 sessionJson 변수에 저장
    def readSession(self, filePath):
        with open(filePath, 'r', encoding='UTF-8') as InSessionFile:
            self.SessionJson = json.load(InSessionFile)

        print(f"[Success] Read the Session File : {filePath}" + "\n")
        return self.SessionJson # 세션 반환
        
        