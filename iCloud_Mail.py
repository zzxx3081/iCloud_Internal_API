import os, sys
import requests, json, urllib3
import sqlite3
from datetime import datetime, timedelta
from time import localtime, strftime, mktime
from termcolor import colored

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Fiddler Local proxy
proxies = {
    'http': 'http://127.0.0.1:8888',
    'https': 'http://127.0.0.1:8888'
}

# Start iCloud Mail Forensics
def Forensic(Account_Session : dict):
    iCloud_Mail_Class = iCloud_Account_Mail(Account_Session)

    while True:
        print(colored("\n[iCloud Mail Menu]", 'yellow'))
        print("iCloud Mail is composed with 3 kinds of category. (INBOX, Sent Messages and Deleted Messages)\n")
        print(colored("[INBOX] It is means a received mailbox, You can check the contents of all received mails.", 'green'))
        print(colored("[Sent Messages] It is means a sent mailbox, You would be able to check the contents of all sent mails.", 'green'))
        print(colored("[Deleted Messages] It is means a trash can, You would be possible to see the list of deleted mails.\n", 'green'))

        print("iCloud mail is consist of Title, Contens and Attachments.")
        print("iCloud breaker exports a \"Database File\" which composed with Tables. (Date, Incoming Mail, Outgoing Mail, Title, Contents, Attachments etc) ")
        print("If you want to download the attachments for some mail, you'll be able to export the file to your input path.")
        print("Furthermore, If you want to see the contents more clearly for some mail, you can download the HTML file to your input path.\n")

        print("#    0. EXIT (Move to Main Category)             #")
        print("#    1. INBOX Forensics                          #")
        print("#    2. Sent Messages Forensics                  #")
        print("#    3. Deleted Messages Forensics               #")
        print("#    4. Show Menu List Again                     #\n")

        Number = int(input(colored("Select Mail Menu: ", 'yellow')))

        if Number == 0:
            print(colored("\n[Move to Main Category]", 'yellow'))
            sys.exit()

        elif Number == 1:
            print(colored("\n[INBOX Forensics ]", 'yellow'))
            iCloud_Mail_Class.INBOX_Request()

        elif Number == 2:
            print(colored("\n[Sent Messages Forensics]", 'yellow'))
            iCloud_Mail_Class.Sent_Messages_Request()

        elif Number == 3:
            print(colored("\n[Deleted Messages Forensics]", 'yellow'))
            iCloud_Mail_Class.Deleted_Messages()

        elif Number == 4:
            continue

        else:
            print("[Invalid Number] Try Again!")


# iCloud Mail Class
class iCloud_Account_Mail:

    # Create "iCloud Mail" Directory to current path
    def __init__(self, Account_Session : dict):
        self.cookies = Account_Session["AccountSessions"] # dict
        self.initDirPath = ".\iCloud Mail"

        if not os.path.exists(self.initDirPath):
            os.makedirs(self.initDirPath)

        # Create Sub Directories in initDirPath (".\iCloud Mail")
        for subDir in ["INBOX", "Sent Messages", "Deleted Messages"]:
            subDirPath = os.path.join(self.initDirPath, subDir)
            if not os.path.exists(subDirPath):
                os.makedirs(subDirPath)

    # Make a Database File in INBOX path
    def INBOX_Request(self):
        # Init DB File
        DBName = datetime.now().strftime("%y%m%d_%H%M%S_INBOX.db")
        PATH = os.path.join(self.initDirPath, "INBOX", DBName)
        connect = sqlite3.connect(PATH)
        cursor = connect.cursor()

        script = """
        CREATE TABLE INBOX(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Received_Timestamp TEXT NOT NULL,
            ThreadId TEXT NOT NULL,
            Senders TEXT NOT NULL,
            Title TEXT NOT NULL,
            Preview TEXT NOT NULL,
            IsSeen TEXT NOT NULL,
            HasAttachment TEXT NOT NULL,
            ToMe TEXT NOT NULL
        );
        """

        cursor.executescript(script)
        connect.commit()

        # Start Request
        try:
            requestURL = "https://p125-mccgateway.icloud.com/mailws2/v1/thread/search"

            header = {
                'Content-Type': 'application/json',
                'Referer': 'https://www.icloud.com/',
                'Accept': '*/*',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.1 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.1',
                'Origin': 'https://www.icloud.com',
            }

            data = {
                "responseType": "THREAD_DIGEST",
                "maxResults": 6,
                "includeFolderStatus": "true",
                "sessionHeaders": {
                    "condstore": 1,
                    "folder": "INBOX",
                    "modseq": "null",
                    "qresync": 1,
                    "threadmode": 1,
                    "threadmodseq": "null"
                }
            }

            postData = json.dumps(data)
            response = requests.post(
                url=requestURL, headers=header, data=postData, cookies=self.cookies, proxies=proxies, verify=False)

            responseJson = json.loads(response.text)

            for mail in responseJson["threadList"]:
                flags = ["True" if _ in mail["flags"] else "False" for _ in ["\\Seen", "\\HasAttachment", "\\ToMe"]]
                KST = self.INBOX_Convert_KST(mail["timestamp"])

                query = """
                INSERT INTO INBOX(
                    Received_Timestamp, ThreadId,
                    Senders, Title, Preview,
                    IsSeen, HasAttachment, ToMe) VALUES (?,?,?,?,?,?,?,?);
                """

                data = (KST, mail["threadId"], 
                    str(mail["senders"])[1:-1], mail["subject"], mail["preview"], 
                    flags[0], flags[1], flags[2]
                )

                cursor.execute(query, data)
                connect.commit()

        except requests.exceptions.RequestException as e:
            print("[Fail] INBOX Request", e)

        connect.close()


    def Sent_Messages_Request(self):
        # Init DB File
        DBName = datetime.now().strftime("%y%m%d_%H%M%S_Sent_Messages.db")
        PATH = os.path.join(self.initDirPath, "Sent Messages", DBName)
        connect = sqlite3.connect(PATH)
        cursor = connect.cursor()

        script = """
        CREATE TABLE Sent_Messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Sent_Timestamp TEXT NOT NULL,
            guid TEXT NOT NULL,
            folder TEXT NOT NULL,
            Recipient TEXT NOT NULL,            
            Sender TEXT NOT NULL,            
            Title TEXT NOT NULL,
            Preview TEXT NOT NULL,
            PreviewId TEXT NOT NULL,
            parts TEXT NOT NULL,
            HasAttachment TEXT NOT NULL
        );
        """

        cursor.executescript(script)
        connect.commit()

        # Start Request
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
                    "guid": "folder:Sent Messages",
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
                    "folder": "folder:Sent Messages",
                    "ids": [ mail["previewId"] for mail in responseJson["result"][1:]]
                }
            }

            postData = json.dumps(preview_data)
            response = requests.post(
                url=requestURL, headers=header, data=postData, cookies=self.cookies, proxies=proxies, verify=False)
            responsePreview = json.loads(response.text)

            # parsing logic
            for mail, preview in zip(responseJson["result"][1:], responsePreview["result"]):
                
                KST = self.Sent_Messages_Convert_KST(mail["sentdate"])
                HasAttachment = "True" if mail.get("hasAttachment") != None else "False"
                
                query = """
                INSERT INTO Sent_Messages(
                    Sent_Timestamp, guid, folder, Recipient, Sender,
                    Title, Preview, PreviewId, 
                    parts, HasAttachment) VALUES (?,?,?,?,?,?,?,?,?,?);
                """

                data = (KST, mail["guid"], mail["folder"], str(mail["to"])[1:-1], mail["from"],
                    mail["subject"], preview["preview"], mail["previewId"],
                    str(mail["parts"]), HasAttachment
                )

                cursor.execute(query, data)
                connect.commit()

        except requests.exceptions.RequestException as e:
            print("[Fail] Sent Messages Request", e)

        connect.close()

    def Deleted_Messages(self):
        pass

    # Convert UTC+9 (INBOX) 1683533164203 -> 2023-05-08 17:06:04
    def INBOX_Convert_KST(self, Timestamp):
        return strftime("%Y-%m-%d %H:%M:%S", localtime(Timestamp / 1000))

    # Convert UTC+9 (INBOX) Mon, 08 May 2023 08:02:16 -0000 -> 2023-05-08 17:02:16
    def Sent_Messages_Convert_KST(self, Timestamp):
        return datetime.strptime(Timestamp, '%a, %d %b %Y %H:%M:%S -0000') + timedelta(hours=9)