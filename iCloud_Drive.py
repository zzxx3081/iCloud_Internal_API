import os, shutil
import requests, json, urllib3
from datetime import datetime, timedelta
from termcolor import colored

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Fiddler Local proxy
proxies = {
    # 'http': 'http://127.0.0.1:8888',
    # 'https': 'http://127.0.0.1:8888'
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
        print("#    2. Show Account Drive Tree                                                 #")
        print("#    3. Show Account Drive Meta Data                                            #")
        print("#    4. Export Drive Files                                                      #")        
        print("#    5. Show Menu List Again                                                    #\n")

        while True:
            Number = input(colored("Select Drive Menu: ", 'yellow'))
            if Number.isdigit() and int(Number) in range(6):
                Number = int(Number)
                break
            print(colored("[Invalid Number] Try Again!\n", 'red'))

        if Number == 0:
            os.system('cls')
            print(colored("\n[Move to Main Category]", 'yellow'))
            break

        elif Number == 1:
            os.system('cls')
            print(colored("\n[iCloud Drive Forensics]", 'yellow'))

            iCloud_Drive_Class.Drive_Live_Request()
            print(colored("[Success] Live Forensics", 'blue'))
            iCloud_Drive_Class.Drive_Trash_Request()
            print(colored(f"[Success] Trash Forensics", 'blue'))

            iCloud_Drive_Class.isExplorer = True # 검사 완료

        elif Number == 2:
            if not iCloud_Drive_Class.isExplorer:
                os.system('cls')
                print(colored("You haven't start [iCloud Drive Forensics] yet.", 'red'))
                print(colored("Please start [iCloud Drive Forensics] First. (Option 1)", 'red'))
                continue

            print(colored("\n[Show Account Drive Tree]", 'yellow'))
            iCloud_Drive_Class.Show_Drive_Tree()

        elif Number == 3:
            if not iCloud_Drive_Class.isExplorer:
                os.system('cls')
                print(colored("You haven't start [iCloud Drive Forensics] yet.", 'red'))
                print(colored("Please start [iCloud Drive Forensics] First. (Option 1)", 'red'))
                continue

            print(colored("\n[Show Account Drive Meta Data]", 'yellow'))
            iCloud_Drive_Class.Show_Drive_Meta()

        elif Number == 4:
            if not iCloud_Drive_Class.isExplorer:
                os.system('cls')
                print(colored("You haven't start [iCloud Drive Forensics] yet.", 'red'))
                print(colored("Please start [iCloud Drive Forensics] First. (Option 1)", 'red'))
                continue

            print(colored("\n[Export Drive Files]", 'yellow'))
            iCloud_Drive_Class.Export_Drive_Files()
        
        elif Number == 5:
            os.system('cls')
            continue

class iCloud_Drive_Node:
    def __init__(self):
        self.Parent = None # iCloud_Drive_Node 루트 초기화
        self.Children = [] # iCloud_Drive_Node List
        self.File = [] # dict List
        self.Folder = {} # dict List


# iCloud Drive Class
class iCloud_Account_Drive:

    # Create "iCloud Drive" Directory to current path
    def __init__(self, Account_Session : dict):
        self.cookies = Account_Session["AccountSessions"] # dict
        self.isExplorer = False # 검사 여부
        self.initDirPath = ".\iCloud Drive"

        if not os.path.exists(self.initDirPath):
            os.makedirs(self.initDirPath)

        self.DriveJson = {} # Drive Data

        for category in ["Live", "Trash"]:
            # Define iCloud Node Class
            self.DriveJson[category] = iCloud_Drive_Node()

            # iCloud Drive\Live, iCloud Drive\Trash 폴더 만들기 + Reset
            subPATH = os.path.join(self.initDirPath, category)

            if not os.path.exists(subPATH):
                os.makedirs(subPATH)
            else:
                shutil.rmtree(subPATH); os.makedirs(subPATH)


    # Get Drive Live Meta Data    
    def Drive_Live_Request(self):
        root = "FOLDER::com.apple.CloudDocs::root"
        self.Drive_Folder(self.DriveJson["Live"], None, root)

    #Get Drive Trash Meta Data
    def Drive_Trash_Request(self):
        root = "TRASH_ROOT"
        self.Drive_Trash_Folder(self.DriveJson["Trash"], root) # 부모노드 존재하지 않음

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
            print(colored("[Fail] Drive Live Request" + str(e), 'red'))
            exit(0)

    # Trash Folder 탐색
    def Drive_Trash_Folder(self, Node: iCloud_Drive_Node, drivewsid: str): # drivewsid: TRASH_ROOT
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
            
            
            # 폴더 정보 없음
            Node.Folder["name"] = "TRASH_ROOT"
            Node.Folder["drivewsid"] = responseJson["drivewsid"]
            Node.Folder["numberOfItems"] = responseJson["numberOfItems"] # 폴더 안에 파일 + 폴더 수


            # 파일 정보만
            for item in responseJson["items"]:
                subFile = {}
                subFile["dateCreated"] = self.Time_Convert(item["dateCreated"])
                subFile["drivewsid"] = item["drivewsid"]
                subFile["docwsid"] = item["docwsid"]
                subFile["zone"] = item["zone"]
                subFile["name"] = item["name"]
                subFile["extension"] = item["extension"]
                subFile["parentId"] = item["parentId"]
                subFile["dateExpiration"] = self.Time_Convert(item["dateExpiration"])
                subFile["isChainedToParent"] = item["isChainedToParent"]
                subFile["dateModified"] = self.Time_Convert(item["dateModified"])
                subFile["dateChanged"] = self.Time_Convert(item["dateChanged"])
                subFile["size"] = item["size"] # Bytes
                subFile["etag"] = item["etag"]
                subFile["restorePath"] = item["restorePath"]
                subFile["shortGUID"] = item["shortGUID"]
                subFile["lastOpenTime"] = self.Time_Convert(item["lastOpenTime"])
                subFile["type"] = item["type"]

                Node.File.append(subFile)

        except requests.exceptions.RequestException as e:
            print(colored("[Fail] Drive Trash Request" + str(e), 'red'))
            exit(0)

    # Show iCloud Drive Tree
    def Show_Drive_Tree(self):

        category = {1:"Live", 2:"Trash"}

        while True:
            print("#    0. EXIT (Move to Drive Category)        #")
            print("#    1. Show Live Tree                       #")
            print("#    2. Show Trash Tree                      #")
            print("#    3. Show Menu List Again                 #\n")

            while True:
                Number = input(colored("Select Drive Menu: ", 'yellow'))
                if Number.isdigit() and int(Number) in range(4):
                    Number = int(Number)
                    break
                print(colored("[Invalid Number] Try Again!\n", 'red'))

            if Number == 0:
                break

            elif Number in [1, 2]:
                print(colored(f"\n[Show {category[Number]}]", 'blue'))
                self.Show_Drive_Meta_Data_Structure(self.DriveJson[category[Number]])

            elif Number == 3:
                os.system('cls')
                continue


    def Show_Drive_Meta_Data_Structure(self, Node : iCloud_Drive_Node, count=0):
        Interval = " " * 4
        newCount = count + 1
        
        # 휴지통이랑 같이 쓰도록!
        if Node.Folder.get("docwsid") == None: NodeID = Node.Folder["drivewsid"]
        else: NodeID = Node.Folder["docwsid"]

        FolderInfo = (Interval * count) + "▶ " + Node.Folder["name"] + "    " + NodeID
        print(FolderInfo)

        for subFolder in Node.Children:
            self.Show_Drive_Meta_Data_Structure(subFolder, newCount)

        for subFile in Node.File:
            subFileName = subFile["name"] + "." + subFile["extension"]
            FileInfo = (Interval * newCount) + "◆ " + subFileName + "    " + subFile["docwsid"]
            print(FileInfo)

        print()

    # Show Drive Meta Data
    def Show_Drive_Meta(self):

        print()

        while True:
            print("#    0. EXIT (Move to Drive Category)            #")
            print("#    1. Search Live Folder Meta Data             #")
            print("#    2. Search Live File Meta Data               #")
            print("#    3. Search Trash File Meta Data              #")
            print("#    4. Search All Meta Data                     #")
            print("#    5. Show Menu List Again                     #\n")

            while True:
                Number = input(colored("Select Drive Menu: ", 'yellow'))
                if Number.isdigit() and int(Number) in range(6):
                    Number = int(Number)
                    break
                print(colored("[Invalid Number] Try Again!\n", 'red'))

            if Number == 0:
                os.system('cls')
                break
            
            elif Number == 1:
                print(colored(f"\n[Search Live Folder Meta Data]", 'blue'))
                data = input(colored("Input Live Folder Name(No extension) or ID(docwid): ", 'yellow'))

                self.MetaFlag = False
                self.Search_Meta_Data_Folder(self.DriveJson["Live"], data)
                
                if not self.MetaFlag:
                    print(colored("Invalid Name or ID(docwid)\n", 'red'))

            elif Number == 2:
                print(colored(f"\n[Search Live File Meta Data]", 'blue'))
                data = input(colored("Input Live File Name(No extension) or ID(docwid): ", 'yellow'))

                self.MetaFlag = False
                self.Search_Meta_Data_File(self.DriveJson["Live"], data)
                if not self.MetaFlag:
                    print(colored("Invalid Name(No extension) or ID(docwid)\n", 'red'))

            elif Number == 3:
                print(colored(f"\n[Search Trash File Meta Data]", 'blue'))
                data = input(colored("Input Trash File Name(No extension) or ID(docwid): ", 'yellow'))

                self.MetaFlag = False
                self.Search_Meta_Data_File(self.DriveJson["Trash"], data)

                if not self.MetaFlag:
                    print(colored("Invalid Name(No extension) or ID(docwid)\n", 'red'))

            elif Number == 4:
                print(colored(f"\n[Show All Live Meta Data]", 'yellow'))
                self.Search_Meta_Data_File_All(self.DriveJson["Live"])
                
                print(colored(f"\n[Show All Trash Meta Data]", 'yellow'))
                self.Search_Meta_Data_File_All(self.DriveJson["Trash"])
                print()

            elif Number == 5:
                os.system('cls')
                continue

    # Node : Live Data or Trash Data, data : Input Name or ID(docwid)
    def Search_Meta_Data_Folder(self, Node: iCloud_Drive_Node, data: str):
        if Node.Folder["name"] == data or Node.Folder["docwsid"] == data:
            print("-" * 80)
            for key, value in Node.Folder.items():
                if key == "Parent": continue
                print(colored(str(key) + " ▶ " + str(value), 'blue'))
            print("-" * 80 + '\n')

            self.MetaFlag = True

        else:
            for subFolder in Node.Children:
                self.Search_Meta_Data_Folder(subFolder, data)
    
    # Node : Live Data or Trash Data, data : Input Name or ID(docwid) 
    def Search_Meta_Data_File(self, Node: iCloud_Drive_Node, data: str):    
        for subFile in Node.File:
            if subFile["name"] == data or subFile["docwsid"] == data:
                print("-" * 80)
                for key, value in subFile.items():
                    print(colored(str(key) + " ▶ " + str(value), 'blue'))
                print("-" * 80 + '\n')

                self.MetaFlag = True
            
        for subFolder in Node.Children:
            self.Search_Meta_Data_File(subFolder, data)

    def Search_Meta_Data_File_All(self, Node: iCloud_Drive_Node):

        print(colored("\n[" + Node.Folder["name"] + "]", 'green'))

        if Node.Parent == None: print(colored("◆ Parent Folder: None", 'green'))
        else: print(colored("◆ Parent Folder: " + Node.Parent.Folder["name"], 'green'))
        
        print(colored("="*80, 'red'))

        # Show Folder
        for key, value in Node.Folder.items():
                if key == "Parent": continue
                print(colored(str(key) + " ▶ " + str(value), 'blue'))

        print()
        print(colored("[Files]", 'green'))
        print("-"*80)

        # Show File
        for subFile in Node.File:
            for key, value in subFile.items():
                print(colored(str(key) + " ▶ " + str(value), 'blue'))

            if subFile == Node.File[-1]: break
            print("-"*80)
            
        print(colored("="*80, 'red'))

        for subFolder in Node.Children:
            self.Search_Meta_Data_File_All(subFolder)


    def Export_Drive_Files(self):
        print()

        while True:
            print("#    0. EXIT (Move to Drive Category)                                #")
            print("#    1. [Live] Export with Name(No extension) or ID(docwid)          #")
            print("#    2. [Live] Export All Files                                      #")
            print("#    3. [Trash] Export with Name(No extension) or ID(docwid)         #")
            print("#    4. [Trash] Export All Files                                     #")
            print("#    5. Show Menu List Again                                         #\n")

            while True:
                Number = input(colored("Select Drive Menu: ", 'yellow'))
                if Number.isdigit() and int(Number) in range(6):
                    Number = int(Number)
                    break
                print(colored("[Invalid Number] Try Again!\n", 'red'))

            if Number == 0:
                os.system('cls')
                break

            elif Number == 1:
                print(colored(f"\n[Live File Export]", 'blue'))
                data = input(colored("Input Live File Name(No extension) or ID(docwid): ", 'yellow'))
                
                # ./iCloud Drive/Live
                self.DriveExportPATH = os.path.join(self.initDirPath, "Live")
                self.ExportFlag = False # 탐지용 플래그 초기화
                self.File_Export(self.DriveJson["Live"], data)
                
                if not self.ExportFlag:
                    print(colored("Invalid Name(No extension) or ID(docwid)\n", 'red'))

            elif Number == 2:
                print(colored(f"\n[Live All File Export]", 'blue'))

                # ./iCloud Drive/Live
                self.DriveExportPATH = os.path.join(self.initDirPath, "Live")
                self.ExportCount = 0
                self.File_Export_All(self.DriveJson["Live"])
                print(colored(f"\n[Complete Export All Live Data]\n", 'yellow'))

            elif Number == 3:
                print(colored(f"\n[Trash File Export]", 'blue'))
                data = input(colored("Input Live File Name(No extension) or ID(docwid): ", 'yellow'))

                # ./iCloud Drive/Live
                self.DriveExportPATH = os.path.join(self.initDirPath, "Trash")
                self.ExportFlag = False # 탐지용 플래그 초기화
                self.File_Export(self.DriveJson["Trash"], data)
                
                if not self.ExportFlag:
                    print(colored("Invalid Name(No extension) or ID(docwid)\n", 'red'))

            elif Number == 4:
                print(colored(f"\n[Trash All File Export]", 'blue'))

                # ./iCloud Drive/Live
                self.DriveExportPATH = os.path.join(self.initDirPath, "Trash")
                self.ExportCount = 0
                self.File_Export_All(self.DriveJson["Trash"])
                print(colored(f"\n[Complete Export All Trash Data]\n", 'yellow'))

            elif Number == 5:
                os.system('cls')
                continue


    def File_Export(self, Node: iCloud_Drive_Node, data):

        Target = list(filter(lambda x: x["name"] == data or x["docwsid"] == data, Node.File))

        if Target != []:

            Download_Json = self.Get_Drive_Download_Token(Target[0]["docwsid"])
            Download_Url = Download_Json["data_token"]["url"]

            header = {
                'Accept': '*/*',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.1 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.1',
            }

            response = requests.get(
                url=Download_Url, headers=header, proxies=proxies, verify=False)
            
            TargetName = Target[0]["name"] + "(" + Target[0]["docwsid"] + ")" + '.' + Target[0]["extension"]
            filePATH = os.path.join(self.DriveExportPATH, TargetName)

            with open(filePATH, "wb") as f:
                f.write(response.content)

            self.ExportFlag = True

            print(colored("\n[Success Export]", 'green'))
            print(colored("▶ " + TargetName, 'blue'))
            print(colored("▶ Export Time: " + datetime.now().strftime('%Y-%m-%dT%H:%M:%S+09:00'), 'blue'))
            print(colored("▶ Path: " + filePATH, 'blue'))
            print("-" * 80 + '\n')
        
        for subFolder in Node.Children:
            self.File_Export(subFolder, data)

    def Get_Drive_Download_Token(self, docwsid: str) -> dict:
        requestURL = "https://p125-docws.icloud.com/ws/com.apple.CloudDocs/download/batch"

        header = {
            'Content-Type': 'application/json',
            'Referer': 'https://www.icloud.com/',
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.1 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.1',
            'Origin': 'https://www.icloud.com',
        }

        data = {
            "document_id" : docwsid
        }

        postData = json.dumps(data)
        response = requests.post(
            url=requestURL, headers=header, data=postData, cookies=self.cookies, proxies=proxies, verify=False)
        
        return json.loads(response.text)[0]


    def File_Export_All(self, Node: iCloud_Drive_Node):

        for subFile in Node.File:
            Download_Json = self.Get_Drive_Download_Token(subFile["docwsid"])

            if Download_Json.get("data_token") == None:
                continue

            Download_Url = Download_Json["data_token"]["url"]

            header = {
                'Accept': '*/*',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.1 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.1',
            }

            response = requests.get(
                url=Download_Url, headers=header, proxies=proxies, verify=False)
            
            TargetName = subFile["name"] + "(" + subFile["docwsid"] + ")" + '.' + subFile["extension"]
            filePATH = os.path.join(self.DriveExportPATH, TargetName)

            with open(filePATH, "wb") as f:
                f.write(response.content)

            self.ExportCount += 1

            print(colored(f"\n[Success Export (Count: {self.ExportCount})]", 'blue'))
            print(colored("▶ " + TargetName, 'blue'))
            print(colored("▶ Export Time: " + datetime.now().strftime('%Y-%m-%dT%H:%M:%S+09:00'), 'blue'))
            print(colored("▶ Path: " + filePATH, 'blue'))
            print("-" * 80)
        
        for subFolder in Node.Children:
            self.File_Export_All(subFolder)


    # UTC -> UTC+9
    def Time_Convert(self, UTC):
        convertTime = datetime.strptime(UTC, '%Y-%m-%dT%H:%M:%SZ')
        convertTime += timedelta(hours=9)
        return convertTime.strftime('%Y-%m-%dT%H:%M:%S+09:00')