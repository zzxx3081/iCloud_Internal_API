import os, shutil
import requests, json, urllib3
import sqlite3
from datetime import datetime, timedelta
from time import mktime
from termcolor import colored

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Fiddler Local proxy
proxies = {
    # 'http': 'http://127.0.0.1:8888',
    # 'https': 'http://127.0.0.1:8888'
}

# Start iCloud Mail Forensics
def Forensic(Account_Session : dict):
    os.system('cls')

    iCloud_Mail_Class = iCloud_Account_Mail(Account_Session)

    while True:
        print(colored("\n[iCloud Mail Menu]", 'yellow'))
        print("iCloud Mail is composed with 3 kinds of category. (INBOX, Sent Messages and Deleted Messages)\n")
        print(colored("[INBOX] It is means a received mailbox, You can check the contents of all received mails.", 'green'))
        print(colored("[Sent Messages] It is means a sent mailbox, You would be able to check the contents of all sent mails.", 'green'))
        print(colored("[Deleted Messages] It is means a trash can, You would be possible to see the list of deleted mails.\n", 'green'))

        print("iCloud mail is consist of Title, Contents and Attachments.")
        print("iCloud breaker exports a \"Database File\" which composed with Tables. (Date, Incoming Mail, Outgoing Mail, Title, Contents, Attachments etc) ")
        print("If you want to download the attachments for some mail, you'll be able to export the file to your input path.")
        print("Furthermore, If you want to see the contents more clearly for some mail, you can download the HTML file to your input path.\n")

        print("#    0. EXIT (Move to Main Category)                                            #")
        print("#    1. Start iCloud Mail Forensics (INBOX, Sent Messages, Deleted Messages)    #")
        print("#    2. Show Account Mail Data                                                  #")
        print("#    3. Export Account Mail Data (Format: DataBase)                             #")
        print("#    4. Export Contents Mail Data                                               #")
        print("#    5. Export Attachment Mail Data                                             #")
        print("#    6. Show Menu List Again                                                    #\n")

        while True:
                Number = input(colored("Select Drive Menu: ", 'yellow'))
                if Number.isdigit() and int(Number) in range(7):
                    Number = int(Number)
                    break
                print(colored("[Invalid Number] Try Again!\n", 'red'))

        if Number == 0:
            os.system('cls')
            print(colored("\n[Move to Main Category]", 'yellow'))
            break

        elif Number == 1:
            os.system('cls')
            print(colored("\n[iCloud Mail Forensics]", 'yellow'))
            iCloud_Mail_Class.Mail_Request()
            
            iCloud_Mail_Class.isExplorer = True # 검사 완료

        elif Number == 2:
            if not iCloud_Mail_Class.isExplorer:
                os.system('cls')
                print(colored("You haven't start [iCloud Mail Forensics] yet.", 'red'))
                print(colored("Please start [iCloud Mail Forensics] First. (Option 1)", 'red'))
                continue

            print(colored("\n[Show Account Mail Data]", 'yellow'))
            iCloud_Mail_Class.Show_Mail_Data() 
        
        elif Number == 3:
            if not iCloud_Mail_Class.isExplorer:
                os.system('cls')
                print(colored("You haven't start [iCloud Mail Forensics] yet.", 'red'))
                print(colored("Please start [iCloud Mail Forensics] First. (Option 1)", 'red'))
                continue

            print(colored("\n[Export Account Mail Data]", 'yellow'))
            iCloud_Mail_Class.Save_Mail_Data()

        elif Number == 4:
            if not iCloud_Mail_Class.isExplorer:
                os.system('cls')
                print(colored("You haven't start [iCloud Mail Forensics] yet.", 'red'))
                print(colored("Please start [iCloud Mail Forensics] First. (Option 1)", 'red'))
                continue

            print(colored("\n[Export Contents Mail Data]", 'yellow'))
            iCloud_Mail_Class.Save_Mail_Contents_Data()            

        elif Number == 5:
            if not iCloud_Mail_Class.isExplorer:
                os.system('cls')
                print(colored("You haven't start [iCloud Mail Forensics] yet.", 'red'))
                print(colored("Please start [iCloud Mail Forensics] First. (Option 1)", 'red'))
                continue

            print(colored("\n[Export Attachment Mail Data]", 'yellow'))
            iCloud_Mail_Class.Save_Mail_Attachment_Data()

        elif Number == 6:
            os.system('cls')
            continue

# iCloud Mail Class
class iCloud_Account_Mail:

    # Create "iCloud Mail" Directory to current path
    def __init__(self, Account_Session : dict):
        self.cookies = Account_Session["AccountSessions"] # dict
        self.isExplorer = False # 검사 여부

        self.initDirPath = ".\iCloud Mail"
        if not os.path.exists(self.initDirPath):
            os.makedirs(self.initDirPath)

        self.MailJson = {} # Mail Data
        for category in ["INBOX", "Sent_Messages", "Deleted_Messages"]:
            self.MailJson[category] = []

    def Mail_Request(self):
        # Start Request
         for category in ["INBOX", "Sent_Messages", "Deleted_Messages"]:
            _category = category.replace('_',' ')

            try:
                requestURL = "https://p31-mailws.icloud.com/wm/message"

                header = {
                    'Content-Type': 'application/json',
                    'Referer': 'https://www.icloud.com/',
                    'Accept': '*/*',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.1 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.1',
                    'Origin': 'https://www.icloud.com',
                }

                data = {
                    "jsonrpc": "2.0",
                    "id": str(int(mktime(datetime.now().timetuple())*1000)) + "/1",
                    "method": "list",
                    "params": {
                        "guid": f"folder:{_category}",
                        "sorttype": "Date",
                        "sortorder": "descending",
                        "searchtype": "null",
                        "searchtext": "null",
                        "requesttype": "index",
                        "responsetype": "hybrid",
                        "selected": 1,
                        "count": 50,
                        "rollbackslot": "0.0"
                    }
                }

                postData = json.dumps(data)
                response = requests.post(
                    url=requestURL, headers=header, data=postData, cookies=self.cookies, proxies=proxies, verify=False)
                responseJson = json.loads(response.text)

                # Second Request to get preview
                preview_data = {
                    "jsonrpc": "2.0",
                    "id": str(int(mktime(datetime.now().timetuple())*1000)) + "/1",
                    "method": "preview",
                    "params": {
                        "folder": f"folder:{_category}",
                        "ids": [ mail["previewId"] for mail in responseJson["result"][1:]]
                    }
                }

                postData = json.dumps(preview_data)
                response = requests.post(
                    url=requestURL, headers=header, data=postData, cookies=self.cookies, proxies=proxies, verify=False)
                responsePreview = json.loads(response.text)

                # parsing logic
                for mail, preview in zip(responseJson["result"][1:], responsePreview["result"]):
                    Mail_Data = {} # dict
                    Mail_Data["Timestamp"] = self.Sent_Messages_Convert_KST(mail["sentdate"])
                    Mail_Data["guid"] = mail["guid"]
                    Mail_Data["folder"] = mail["folder"]
                    Mail_Data["Recipient"] = mail["to"]
                    Mail_Data["Sender"] = mail["from"]
                    Mail_Data["Title"] = mail["subject"]
                    Mail_Data["PreviewId"] = mail["previewId"]
                    Mail_Data["Preview"] = preview["preview"]
                    Mail_Data["HasAttachment"] = "True" if mail.get("hasAttachment") != None else "False"

                    # Attachment parsing        
                    Mail_Data["parts"] = []

                    for attachment in mail["parts"]:
                        part = {}
                        part["pguid"] = attachment["guid"]
                        part["datatype"] = attachment["datatype"]
                        part["name"] = attachment.get("name")
                        part["url"] = attachment["url"]
                        part["size"] = attachment["size"]
                        Mail_Data["parts"].append(part)

                    Mail_Data["NumOfAttachment"] = len(Mail_Data["parts"]) - 1
                    
                    self.MailJson[category].append(Mail_Data)

                print(colored(f"[Success] {category} Forensics", 'blue'))

            except requests.exceptions.RequestException as e:
                print(f"[Fail] {category} Request", e)

    def Show_Mail_Data(self):

        if (self.MailJson["INBOX"], self.MailJson["Sent_Messages"], self.MailJson["Deleted_Messages"]) == ([], [], []):
            print("[Empty Mailbox] Check whether you perform \"Start iCloud Mail Forensics (INBOX, Sent Messages, Deleted Messages)\" menu.\n")
            return

        category = {1:"INBOX", 2:"Sent_Messages", 3:"Deleted_Messages"}

        while True:
            print("#    0. EXIT (Move to Mail Category)         #")
            print("#    1. Show INBOX                           #")
            print("#    2. Show Sent Messages                   #")
            print("#    3. Show Deleted Messages                #")
            print("#    4. Show Menu List Again                 #\n")

            while True:
                Number = input(colored("Select Drive Menu: ", 'yellow'))
                if Number.isdigit() and int(Number) in range(5):
                    Number = int(Number)
                    break
                print(colored("[Invalid Number] Try Again!\n", 'red'))

            if Number == 0:
                os.system('cls')
                break

            elif Number in [1, 2, 3]:
                print(colored(f"\n[Show {category[Number]}]", 'blue'))
                print(f"\n■ {category[Number]} Count:", len(self.MailJson[category[Number]]))
                print("\n" + "-" * 85 +"\n")

                for i, mail in enumerate(self.MailJson[category[Number]]):
                    print("● Index:", i+1)
                    for key, value in mail.items():
                        print('●', key+':', value)
                    print("\n" + "-" * 85 +"\n")


            elif Number == 4:
                os.system('cls')
                continue

    def Save_Mail_Data(self):

        if (self.MailJson["INBOX"], self.MailJson["Sent_Messages"], self.MailJson["Deleted_Messages"]) == ([], [], []):
            print("[Empty Mailbox] Check whether you perform \"Start iCloud Mail Forensics (INBOX, Sent Messages, Deleted Messages)\" menu.\n")
            return

        # Init DB File
        DBName = "iCloud_Mail.db"
        PATH = os.path.join(self.initDirPath, DBName)
        connect = sqlite3.connect(PATH)
        cursor = connect.cursor()
        
        for Table in ["INBOX", "Sent_Messages", "Deleted_Messages"]:

            # Create DB Table
            script = f"""
            DROP TABLE IF EXISTS {Table};

            CREATE TABLE {Table}(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Timestamp TEXT NOT NULL,
                guid TEXT NOT NULL,
                folder TEXT NOT NULL,
                Recipient TEXT NOT NULL,            
                Sender TEXT NOT NULL,            
                Title TEXT NOT NULL,
                PreviewId TEXT NOT NULL,
                Preview TEXT NOT NULL,
                HasAttachment TEXT NOT NULL,
                NumOfAttachment TEXT NOT NULL,
                Parts TEXT NOT NULL
            );
            """

            cursor.executescript(script)
            connect.commit()

            # Insert Mail Record
            Table_Query = f"""
            INSERT INTO {Table}(
                Timestamp, guid, folder, Recipient,
                Sender, Title, PreviewId, Preview, 
                HasAttachment, NumOfAttachment, Parts)
                VALUES (?,?,?,?,?,?,?,?,?,?,?);
            """

            Table_Data = []

            for mail in self.MailJson[Table]:
                data = (
                    mail["Timestamp"], mail["guid"], mail["folder"], str(mail["Recipient"]),
                    mail["Sender"], mail["Title"], mail["PreviewId"], mail["Preview"],
                    mail["HasAttachment"], str(mail["NumOfAttachment"]), str(mail["parts"])
                )
                Table_Data.append(data)

            cursor.executemany(Table_Query, Table_Data)
            connect.commit()

        print(colored(f"[Success] Export the iCloud Mail DataBase File : {PATH}" + "\n", 'blue'))
        connect.close()

    def Save_Mail_Attachment_Data(self):

        if (self.MailJson["INBOX"], self.MailJson["Sent_Messages"], self.MailJson["Deleted_Messages"]) == ([], [], []):
            print("[Empty Mailbox] Check whether you perform \"Start iCloud Mail Forensics (INBOX, Sent Messages, Deleted Messages)\" menu.\n")
            return


        PATH = os.path.join(self.initDirPath, ".\iCloud Mail Attachment")
        if not os.path.exists(PATH):
            os.makedirs(PATH)
        else:
            shutil.rmtree(PATH); os.makedirs(PATH)
        
        # Make Attachment sub Directory
        for category in ["INBOX", "Sent_Messages", "Deleted_Messages"]:
            print(colored(f"[Start] Export {category} Attachments", 'blue'))

            subPATH = os.path.join(PATH, category)
            if not os.path.exists(subPATH):
                os.makedirs(subPATH)
            else:
                shutil.rmtree(subPATH); os.makedirs(subPATH)

            for mail in self.MailJson[category]:
                if mail["NumOfAttachment"] != 0:
                    for count in range(mail["NumOfAttachment"]):
                        requestURL = "https://p31-mailws.icloud.com" + mail["parts"][count + 1]["url"]

                        header = {
                            'Content-Type': 'application/json',
                            'Referer': 'https://www.icloud.com/',
                            'Accept': '*/*',
                            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.1 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.1',
                            'Origin': 'https://www.icloud.com',
                        }

                        response = requests.get(url=requestURL, headers=header, cookies=self.cookies, proxies=proxies, verify=False)

                        filePATH = os.path.join(subPATH, mail["parts"][count + 1]["name"])

                        with open(filePATH, 'wb') as f:
                            f.write(response.content)


    def Save_Mail_Contents_Data(self):


        if (self.MailJson["INBOX"], self.MailJson["Sent_Messages"], self.MailJson["Deleted_Messages"]) == ([], [], []):
            print("[Empty Mailbox] Check whether you perform \"Start iCloud Mail Forensics (INBOX, Sent Messages, Deleted Messages)\" menu.\n")
            return

        PATH = os.path.join(self.initDirPath, ".\iCloud Mail Contents")

        if not os.path.exists(PATH):
            os.makedirs(PATH)
        else:
            shutil.rmtree(PATH); os.makedirs(PATH)

        # Make Attachment sub Directory
        for category in ["INBOX", "Sent_Messages", "Deleted_Messages"]:
            print(colored(f"[Start] Export {category} Contents", 'blue'))

            subPATH = os.path.join(PATH, category)
            if not os.path.exists(subPATH):
                os.makedirs(subPATH)
            else:
                shutil.rmtree(subPATH); os.makedirs(subPATH)

            for mail in self.MailJson[category]:
                requestURL = "https://p31-mailws.icloud.com/wm/message"
                # requestURL = "https://p31-mailws.icloud.com" + mail["parts"][count + 1]["url"]

                header = {
                    'Content-Type': 'application/json',
                    'Referer': 'https://www.icloud.com/',
                    'Accept': '*/*',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.1 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.1',
                    'Origin': 'https://www.icloud.com',
                }

                data = {
                    "jsonrpc": "2.0",
                    "id": str(int(mktime(datetime.now().timetuple())*1000)) + "/1",
                    "method": "get",
                    "params": {
                        "guid": mail["guid"],
                        "parts": [
                            mail["parts"][0]["pguid"]
                        ]
                    },
                    "dontMarkAsRead": "true"
                }

                postData = json.dumps(data)
                response = requests.post(url=requestURL, headers=header, data=postData, cookies=self.cookies, proxies=proxies, verify=False)

                mailContent = response.json()["result"][0]["parts"][0]["content"]

                filePATH = os.path.join(subPATH, mail["Title"] + ".HTML")

                with open(filePATH, 'w', encoding='utf-8') as f:
                    f.write(mailContent)

    # Convert UTC+9 Mon, 08 May 2023 08:02:16 -0000 -> 2023-05-08 17:02:16
    def Sent_Messages_Convert_KST(self, Timestamp):
        Timestamp = Timestamp[:31] if len(Timestamp) > 31 else Timestamp
        convertTime = datetime.strptime(Timestamp[:-6], '%a, %d %b %Y %H:%M:%S')
        return convertTime + timedelta(hours=9-int(Timestamp[-5:-2]))