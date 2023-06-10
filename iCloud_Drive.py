import os
import requests, json, urllib3
from datetime import datetime, timedelta
from termcolor import colored

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Fiddler Local proxy
proxies = {
    'http': 'http://127.0.0.1:8888',
    'https': 'http://127.0.0.1:8888'
}


def Forensic(Account_Session : dict):
    os.system('cls')

    iCloud_Drive_Class = iCloud_Account_Drive(Account_Session)

    while True:
        print(colored("\n[iCloud Drive Menu]", 'yellow'))
        print("iCloud Drive is composed with 2 kinds of category. (Live, Trash)\n")
        print(colored("[Live] It means feature that retrieves information about files and folders that have not been deleted in iCloud Drive.", 'green'))
        print(colored("[Trash] It means feature that retrieves information about files and folders that have been deleted in iCloud Drive.\n", 'green'))

        print("#    0. EXIT (Move to Main Category)                                            #")
        print("#    1. Start iCloud Drive Forensics (Live, Trash)                              #")
        print("#    2. Show Account Drive Data                                                 #")
        print("#    3. Show Menu List Again                                                    #\n")

        Number = int(input(colored("Select Drive Menu: ", 'yellow')))

        if Number == 0:
            os.system('cls')
            print(colored("\n[Move to Main Category]", 'yellow'))
            break

        elif Number == 1:
            print(colored("\n[iCloud Drive Forensics]", 'yellow'))

            iCloud_Drive_Class.Drive_Live_Request()
            print(colored("[Success] Live Forensics", 'blue'))
            iCloud_Drive_Class.Drive_Trash_Request()
            print(colored(f"[Success] Trash Forensics", 'blue'))

        elif Number == 2:
            print(colored("\n[Show Account Drive Data]", 'yellow'))
            iCloud_Drive_Class.Show_Drive_Data()

        elif Number == 3:
            os.system('cls')
            continue

        else:
            print("[Invalid Number] Try Again!")







    # cookies = Account_Session["AccountSessions"] # dict
    # requestURL = "https://p125-drivews.icloud.com/retrieveItemDetailsInFolders"
    # requestURL = "https://p125-drivews.icloud.com/retrieveItemDetails"

    # header = {
    #     'Content-Type': 'application/json',
    #     'Referer': 'https://www.icloud.com/',
    #     'Accept': '*/*',
    #     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.1 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.1',
    #     'Origin': 'https://www.icloud.com',
    # }

    # data = [{
    #     "drivewsid":"FOLDER::com.apple.CloudDocs::root",
    #     "partialData":"false",
    #     "includeHierarchy":"true"
    # }]

    # data = {
    #     "items" : [{"drivewsid" : "FILE::com.apple.CloudDocs::125B4B6C-B330-40A6-852E-F283CD4249F6"}]
    # }

    # postData = json.dumps(data)
    # response = requests.post(
    #     url=requestURL, headers=header, data=postData, cookies=cookies, proxies=proxies, verify=False)
    # responseJson = json.loads(response.text)
    # print(responseJson)


class iCloud_Drive_Node:
    def __init__(self):
        self.Parent = None # iCloud_Drive_Node
        self.Children = [] # iCloud_Drive_Node List
        self.File = [] # dict List
        self.Folder = {} # dict List


# iCloud Drive Class
class iCloud_Account_Drive:

    # Create "iCloud Drive" Directory to current path
    def __init__(self, Account_Session : dict):
        self.cookies = Account_Session["AccountSessions"] # dict

        self.initDirPath = ".\iCloud Drive"
        if not os.path.exists(self.initDirPath):
            os.makedirs(self.initDirPath)

        self.DriveJson = {} # Drive Data

        for category in ["Live", "Trash"]:
            # Define iCloud Node Class
            self.DriveJson[category] = iCloud_Drive_Node()

    # Get Drive Live Meta Data    
    def Drive_Live_Request(self):
        root = "FOLDER::com.apple.CloudDocs::root"
        self.Drive_Folder(self.DriveJson["Live"], None, root)

        # print(json.dumps(self.DriveJson["Live"].Folder, indent=4, ensure_ascii=False))
        # print(json.dumps(self.DriveJson["Live"].File, indent=4, ensure_ascii=False))

    #Get Drive Trash Meta Data
    def Drive_Trash_Request(self):
        # root = ""
        # self.Drive_Folder(self.DriveJson["Trash"], None, root)
        pass

    # Node: Present, Parent: Parent Node, drivewsid: Folder ID
    def Drive_Folder(self, Node: iCloud_Drive_Node, Parent: iCloud_Drive_Node, drivewsid: str):

        try:
            requestURL = "https://p125-drivews.icloud.com/retrieveItemDetailsInFolders?appIdentifier=iclouddrive"

            header = {
                'Content-Type': 'application/json',
                'Referer': 'https://www.icloud.com/',
                'Accept': '*/*',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.1 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.1',
                'Origin': 'https://www.icloud.com',
            }

            data = [{
                "drivewsid": drivewsid,
                "partialData":"false",
                "includeHierarchy":"true"
            }]

            postData = json.dumps(data)
            response = requests.post(
                url=requestURL, headers=header, data=postData, cookies=self.cookies, proxies=proxies, verify=False)
            responseJson = json.loads(response.text)[0]

            # 현재 폴더 정보
            Node.Folder["dateCreated"] = self.Time_Convert(responseJson["dateCreated"])
            Node.Folder["drivewsid"] = responseJson["drivewsid"]
            Node.Folder["docwsid"] = responseJson["docwsid"]
            Node.Folder["zone"] = responseJson["zone"]
            Node.Folder["name"] = responseJson["name"]
            Node.Folder["hierarchy"] = responseJson["hierarchy"]
            Node.Folder["etag"] = responseJson["etag"]
            Node.Folder["type"] = responseJson["type"]
            Node.Folder["assetQuota"] = responseJson["assetQuota"] # 폴더 내 파일의 모든 크기 합산 바이트
            Node.Folder["fileCount"] = responseJson["fileCount"] # 하위 폴더까지 포함한 모든 파일 수
            Node.Folder["shareCount"] = responseJson["shareCount"] # 공유 파일 수
            Node.Folder["shareAliasCount"] = responseJson["shareAliasCount"] # 공유 별명 수
            Node.Folder["directChildrenCount"] = responseJson["directChildrenCount"] # 폴더 아래 하위 노드들의 수
            Node.Folder["numberOfItems"] = responseJson["numberOfItems"] # 폴더 안에 파일 + 폴더 수

            Node.Folder["Parent"] = Parent # Class 연결

            if Node.Folder.get("parentId") == None:
                Node.Folder["parentName"] = "None"
                Node.Folder["isChainedToParent"] = "False"
                Node.Folder["name"] = "root"
            else:
                Node.Folder["parentName"] = Parent.Folder["name"]
            
            for item in responseJson["items"]:

                if item["type"] == "FOLDER":

                    subFolder = iCloud_Drive_Node()
                    subFolder.Parent = Node

                    subFolder.Folder["drivewsid"] = item["drivewsid"]
                    subFolder.Folder["parentId"] = item["parentId"]
                    subFolder.Folder["isChainedToParent"] = item["isChainedToParent"]

                    # recursion
                    self.Drive_Folder(subFolder, subFolder.Parent, subFolder.Folder["drivewsid"])
                    Node.Children.append(subFolder)
                
                # 현재 파일 정보
                else:

                    subFile = {}

                    subFile["dateCreated"] = self.Time_Convert(item["dateCreated"])
                    subFile["drivewsid"] = item["drivewsid"]
                    subFile["docwsid"] = item["docwsid"]
                    subFile["zone"] = item["zone"]
                    subFile["name"] = item["name"]
                    subFile["extension"] = item.get("extension")
                    subFile["parentId"] = item["parentId"]
                    subFile["parentName"] = Node.Folder["parentName"]
                    subFile["isChainedToParent"] = item["isChainedToParent"]
                    subFile["dateModified"] = self.Time_Convert(item["dateModified"])
                    subFile["dateChanged"] = self.Time_Convert(item["dateChanged"])
                    subFile["size"] = item["size"] # Bytes
                    subFile["etag"] = item["etag"]
                    subFile["lastOpenTime"] = self.Time_Convert(item["lastOpenTime"])
                    subFile["type"] = item["type"]

                    Node.File.append(subFile)


        except requests.exceptions.RequestException as e:
            print("[Fail] Drive Live Request", e)

    # Show iCloud Drive Meta Data
    def Show_Drive_Data(self):

        category = {1:"Live", 2:"Trash"}

        while True:
            print("#    0. EXIT (Move to Drive Category)         #")
            print("#    1. Show Live                            #")
            print("#    2. Show Trash                           #")
            print("#    3. Show Menu List Again                 #\n")

            Number = int(input(colored("Select Show Drive Menu: ", 'yellow')))

            if Number == 0:
                os.system('cls')
                break

            elif Number in [1, 2]:
                os.system('cls')
                print(colored(f"\n[Show {category[Number]}]", 'blue'))
                self.Show_Drive_Meta_Data_Structure(self.DriveJson[category[Number]])

            elif Number == 3:
                os.system('cls')
                continue

            else:
                print("[Invalid Number] Try Again!")


    def Show_Drive_Meta_Data_Structure(self, Node : iCloud_Drive_Node, count=0):
        Interval = " " * 4
        newCount = count + 1
        
        FolderInfo = (Interval * count) + "▶ " + Node.Folder["name"] + "    " + Node.Folder["docwsid"]
        print(FolderInfo)

        for subFolder in Node.Children:
            self.Show_Drive_Meta_Data_Structure(subFolder, newCount)

        for subFile in Node.File:
            FileInfo = (Interval * newCount) + "◆ " + subFile["name"] + "    " + subFile["docwsid"]
            print(FileInfo)

        print()

    # UTC -> UTC+9
    def Time_Convert(self, UTC):
        convertTime = datetime.strptime(UTC, '%Y-%m-%dT%H:%M:%SZ')
        convertTime += timedelta(hours=9)
        return convertTime.strftime('%Y-%m-%dT%H:%M:%S+09:00')