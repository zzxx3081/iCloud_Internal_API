import os
import sys
import requests
import json
import urllib3
import msvcrt
from iCloud_Session import Session
from termcolor import colored

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Fiddler Local proxy
proxies = {
    'http': 'http://127.0.0.1:8888',
    'https': 'http://127.0.0.1:8888'
}


# Get a new iCloud Session Data through Login Data
def Authentication_NewToken() -> dict:

    print("To acquire a new Session Informaion from iCloud Account Management Server, You need to input any iCloud Account Information (such as ID, PW, TrustToken ..)")
    print("Moreover, If you know \"TrustToken\" of the iCloud Account, You'll be able to bypass the Two-Factor-Authentication.")
    print("The iCloud Login process requires Two-Factor-Authentication by default.")
    print("In order to success the Two-Factor-Authentication, You should input the 6-digit Security Code which can get from Apple Device connected by the iCloud Account.\n")

    print(colored("Submit your iCloud Account Information.", 'green'))
    iCloud_ID, iCloud_PW = input_iCloud_Credential()

    while True:
        print(colored("\nDo you know the Account's TrustToken? (Y/N)", 'yellow'))
        Answer = input(colored("Answer: ", 'yellow'))

        if Answer.lower() == 'y':
            print(colored("\nInput the Account's TrustToken.", 'yellow'))
            print(colored(
                "[Reference] If you submit the Invalid TrustToken, you'll move to Two-Factor-Authentication process Automatically.", 'green'))
            TrustToken = input(colored("TrustToken: ", 'yellow'))
            break
        elif Answer.lower() == 'n':
            print(colored(
                "\n[Default] You need to perform the Two-Factor-Authentication\n", 'yellow'))
            break
        else:
            print(colored("\n[Invalid Input] Try Again!\n", 'yellow'))

    # Login Based Session Authentication Start!
    iCloud_Login_Class = iCloud_Account_Session(iCloud_ID, iCloud_PW)

    # Check whether to save the Session Data or not
    while True:
        print("\nIt is recommended to save the Session Data to prevent the Account block from iCloud Server.")
        print(colored("Do you want to save the Session Data? (Y/N)", 'yellow'))
        Answer = input(colored("Answer: ", 'yellow'))

        if Answer.lower() == 'y':
            print(colored("\nSubmit the Output Path to save the Session Data.", 'green'))
            iCloud_Session_Path = dequote(
                input(colored("iCloud Session Path: ", 'yellow')))

            while not os.path.exists(iCloud_Session_Path):
                print(colored("\n[Invalid Path] Try Again!\n", 'yellow'))
                iCloud_Session_Path = input(
                    colored("iCloud Session Path: ", 'yellow'))

            iCloud_Login_Class.saveSession(iCloud_Session_Path)
            break

        elif Answer.lower() == 'n':
            print(colored(
                "\n[warning]If the program shut down, You can't use the iCloud Session Data again.", 'red'))
            break
        else:
            print(colored("\n[Invalid Input] Try Again!\n", 'yellow'))

    return iCloud_Login_Class.getSesssion()


# Get a old iCloud Session Data through Local Session File
def Authentication_FileToken() -> dict:

    print("To acquire a old Session Informaion from Local Session File, You need to input the Session File Path.\n")
    print(colored("Submit the Full Path about Local Session File (Format : Json).", 'green'))
    Local_Session_Path = dequote(
        input(colored("Local Session File Path: ", 'yellow')))

    while not os.path.exists(Local_Session_Path):
        print(colored("\n[Invalid Path] Try Again!\n", 'yellow'))
        Local_Session_Path = input(
            colored("Local Session File Path: ", 'yellow'))

    iCloud_Session_Class = Session()

    return iCloud_Session_Class.readSession(Local_Session_Path)



def input_iCloud_Credential():
    iCloud_ID = input(colored("iCloud ID: ", 'yellow'))
    iCloud_PW = ""
    print(colored("iCloud PW: ", 'yellow'), end='', flush=True)
    len_Of_PW = 0

    while True:
        pwChar = msvcrt.getch()

        # Case of newline
        if pwChar == b'\r':
            print()
            break

        # Case of backspace
        elif pwChar == b'\b':
            if len_Of_PW < 1:
                pass
            else:
                msvcrt.putch(b'\b')
                msvcrt.putch(b' ')
                msvcrt.putch(b'\b')
                iCloud_PW = iCloud_PW[:-1]
                len_Of_PW -= 1

        # [Arrow] Key Exception
        elif pwChar == b'\xe0':
            msvcrt.getch()

        # [Tab] Key Exception
        elif pwChar in [b'\t']:
            continue

        # [Ctrl + z] or [Ctrl + c] -> Shut Down
        elif pwChar in [b'\x03', b'\x1a']:
            print(colored("\n[Shut Down]", 'yellow'))
            sys.exit()

        else:
            print("●", end='', flush=True)
            iCloud_PW += pwChar.decode("utf-8")
            len_Of_PW += 1

    return iCloud_ID, iCloud_PW

# Remove input "\'" or "\""  (ex: 'path' -> path)
def dequote(s):
    if (s[0] == s[-1]) and s.startswith(("'", '"')):
        return s[1:-1]
    return s


# iCloud Auth Class <- Inheritance iCloud_Session Class
class iCloud_Account_Session(Session):

    # Require iCloud ID, PW and TrustToken (Default Empty String)
    def __init__(self, ID, Password, TrustToken=''):

        super().__init__()  # iCloud_Session Class Init

        # iCloud Account Information
        self.SessionJson['AccountInfo'] = {
            'iCloud ID': ID,
            'iCloud PW': Password
        }

        # iCloud Headers
        self.SessionJson['AccountHeaders'] = {}

        # iCloud Cookies & Sessions
        self.SessionJson['AccountSessions'] = {}

        # Start the First Auth
        self.First_Signin_Request(TrustToken)

    # First Auth Signin Request

    def First_Signin_Request(self, TrustToken=''):
        try:
            requestURL = "https://idmsa.apple.com/appleauth/auth/signin"

            header = {
                'Content-Type': 'application/json',
                'Referer': 'https://idmsa.apple.com/appleauth/auth/signin',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.1 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.1',
                'Origin': 'https://idmsa.apple.com',
                'X-Requested-With': 'XMLHttpRequest',
                'X-Apple-Widget-Key': 'd39ba9916b7251055b22c7f910e2ea796ee65e98b2ddecea8f5dde8d9d1a815d'
            }

            data = {
                'accountName': self.SessionJson['AccountInfo']['iCloud ID'],
                'password': self.SessionJson['AccountInfo']['iCloud PW'],
                'rememberMe': True,
                'trustTokens': [TrustToken]
            }

            postData = json.dumps(data)
            response = requests.post(
                url=requestURL, headers=header, data=postData, proxies=proxies, verify=False)

            # Get First Auth Token
            self.SessionJson['AccountHeaders']['scnt'] = response.headers['scnt']
            self.SessionJson['AccountHeaders']['X-Apple-Auth-Attributes'] = response.headers['X-Apple-Auth-Attributes']
            self.SessionJson['AccountHeaders']['X-Apple-Widget-Key'] = 'd39ba9916b7251055b22c7f910e2ea796ee65e98b2ddecea8f5dde8d9d1a815d'
            self.SessionJson['AccountHeaders']['X-Apple-Session-Token'] = response.headers['X-Apple-Session-Token']
            self.SessionJson['AccountHeaders']['X-Apple-ID-Account-Country'] = response.headers['X-Apple-ID-Account-Country']
            self.SessionJson['AccountHeaders']['X-Apple-ID-Session-Id'] = response.headers['X-Apple-ID-Session-Id']

            # Check whether to Second Auth (If the TrustToken is empty or invalid than need to perform the Two-Factor-Authentication process)
            # If the Two-Factor-Authentication process is required, this value is setted true
            if response.headers.get('X-Apple-TwoSV-Trust-Eligible') != None:
                self.Second_Securitycode_Request()  # Update the X-Apple-Session-Token
                self.Get_TrustToken_Request()  # Get TrustToken
                self.AccountLogin_Request()  # Get WEB AUTH, PCS cookies

            else:
                self.SessionJson['AccountHeaders']['X-Apple-TwoSV-Trust-Token'] = TrustToken
                self.AccountLogin_Request()  # Get WEB AUTH, PCS cookies

        except requests.exceptions.RequestException as e:
            print("[Fail] First Auth Signin Request", e)

    # Second Auth Securitycode Request

    def Second_Securitycode_Request(self):
        try:
            requestURL = "https://idmsa.apple.com/appleauth/auth/verify/trusteddevice/securitycode"

            header = {
                'Content-Type': 'application/json',
                'Referer': 'https://idmsa.apple.com/',
                'scnt': self.SessionJson['AccountHeaders']['scnt'],
                'X-Apple-ID-Session-Id': self.SessionJson['AccountHeaders']['X-Apple-ID-Session-Id'],
                'X-Apple-Widget-Key': self.SessionJson['AccountHeaders']['X-Apple-Widget-Key'],
            }

            data = {
                'securityCode': {
                    'code': input(colored("Security Code(6-digit): ", 'yellow'))
                }
            }

            postData = json.dumps(data)

            # If allow the redirect, can't get updated X-Apple-Session-Token
            response = requests.post(url=requestURL, headers=header, data=postData,
                                     proxies=proxies, verify=False, allow_redirects=False)

            # After the Second Auth, update the X-Apple-Session-Token
            self.SessionJson['AccountHeaders']['X-Apple-Session-Token'] = response.headers['X-Apple-Session-Token']

        except requests.exceptions.RequestException as e:
            print("[Fail] Second Auth Securitycode Reqeust", e)

    # Get TrustToken

    def Get_TrustToken_Request(self):
        try:
            requestURL = "https://idmsa.apple.com/appleauth/auth/2sv/trust"

            header = {
                'Content-Type': 'application/json',
                'Referer': 'https://idmsa.apple.com/',
                'scnt': self.SessionJson['AccountHeaders']['scnt'],
                'X-Apple-ID-Session-Id': self.SessionJson['AccountHeaders']['X-Apple-ID-Session-Id'],
                'X-Apple-Widget-Key': self.SessionJson['AccountHeaders']['X-Apple-Widget-Key'],
            }

            response = requests.get(
                url=requestURL, headers=header, proxies=proxies, verify=False)

            # Aquire the TrusToken and updated X-Apple-Session-Token
            self.SessionJson['AccountHeaders']['X-Apple-Session-Token'] = response.headers['X-Apple-Session-Token']
            self.SessionJson['AccountHeaders']['X-Apple-TwoSV-Trust-Token'] = response.headers['X-Apple-TwoSV-Trust-Token']

        except requests.exceptions.RequestException as e:
            print("[Fail] TrustToken Reqeust", e)

    # Get the Auth cookis about PCS and WEB AUTH (AccountLogin Request)

    def AccountLogin_Request(self):

        try:
            requestURL = "https://setup.iCloud.com/setup/ws/1/accountLogin"

            header = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.1 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.1',
                'Referer': 'https://www.icloud.com/',
                'Origin': 'https://www.icloud.com',
                'Connection': 'keep-alive',
            }

            data = {
                'dsWebAuthToken': self.SessionJson['AccountHeaders']['X-Apple-Session-Token'],
                'accountCountryCode': self.SessionJson['AccountHeaders']['X-Apple-ID-Account-Country'],
                'extended_login': "true"
            }

            postData = json.dumps(data)
            response = requests.post(
                url=requestURL, headers=header, data=postData, proxies=proxies, verify=False)

            # After the Second Auth, get the PCS, WEB-AUTH cookies
            for cookie in response.cookies:
                self.SessionJson['AccountSessions'][cookie.name] = cookie.value

            # Get the personal information
            responseJson = json.loads(response.text)
            self.SessionJson['AccountInfo']['User Name'] = responseJson['dsInfo']['fullName']
            self.SessionJson['AccountInfo']['Dsid'] = responseJson['dsInfo']['dsid']
            self.SessionJson['AccountInfo']['Country Code'] = responseJson['dsInfo']['countryCode']
            self.SessionJson['AccountInfo']['Time Zone'] = responseJson['requestInfo']['timeZone']

        except requests.exceptions.RequestException as e:
            print("[Fail] AccountLogin Reqeust", e)
