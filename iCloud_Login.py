import os, requests, json, urllib3
from iCloud_Session import Session
from termcolor import colored

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
    iCloud_ID = input(colored("iCloud ID: ", 'yellow'))
    iCloud_PW = input(colored("iCloud PW: ", 'yellow'))


    while True:
        print(colored("\nDo you know the Account's TrustToken? (Y/N)", 'yellow'))
        Answer = input(colored("Answer: ", 'yellow'))

        if Answer.lower() == 'y':
            print(colored("\nInput the Account's TrustToken.", 'yellow'))
            print(colored("[Reference] If you submit the Invalid TrustToken, you'll move to Two-Factor-Authentication process Automatically.", 'green'))
            TrustToken = input(colored("TrustToken: ", 'yellow'))
            break
        elif Answer.lower() == 'n':
            print(colored("\n[Default] You need to perform the Two-Factor-Authentication\n", 'yellow'))
            break
        else:
            print(colored("\n[Invalid Input] Try Again!\n", 'yellow'))

    
    # Login Based Session Authentication Start!
    iCloud_Login_Class = iCloud_Auth_Session(iCloud_ID, iCloud_PW)

    # Check whether to save the Session Data or not
    while True:
        print("\nIt is recommended to save the Session Data to prevent the Account block from iCloud Server.")
        print(colored("Do you want to save the Session Data? (Y/N)", 'yellow'))
        Answer = input(colored("Answer: ", 'yellow'))

        if Answer.lower() == 'y':
            print(colored("\nSubmit the Output Path to save the Session Data.", 'yellow'))
            iCloud_Session_Path = input(colored("iCloud Session Path: ", 'yellow'))

            while not os.path.exists(iCloud_Session_Path):
                print(colored("\n[Invalid Path] Try Again!\n", 'yellow'))
                iCloud_Session_Path = input(colored("iCloud Session Path: ", 'yellow'))

            iCloud_Login_Class.saveSession(iCloud_Session_Path)
            break
        
        elif Answer.lower() == 'n':
            print(colored("\n[warning]If the program shut down, You can't use the iCloud Session Data again.", 'red'))
            break
        else:
            print(colored("\n[Invalid Input] Try Again!\n", 'yellow'))

    return iCloud_Login_Class.getSesssion()



# Get a old iCloud Session Data through Local Session File
def Authentication_FileToken() -> dict:

    print("To acquire a old Session Informaion from Local Session File, You need to input the Session File Path.") 
    print(colored("Submit the Full Path about Local Session File (Format : Json).", 'green'))
    Local_Session_Path = input(colored("Local Session File Path: ", 'yellow'))

    while not os.path.exists(Local_Session_Path):
        print(colored("\n[Invalid Path] Try Again!\n", 'yellow'))
        Local_Session_Path = input(colored("Local Session File Path: ", 'yellow'))

    iCloud_Session_Class = Session()

    return iCloud_Session_Class.readSession(Local_Session_Path)



# iCloud 인증 클래스, 저장용 세션 클래스를 상속받음 (인증할 때마다 세션 및 토큰을 동적으로 수집함)
class iCloud_Auth_Session(Session):

    # iCloud 아이디, 비밀번호, TrustToken 입력 받기
    def __init__(self, ID, Password, TrustToken = ''):

        super().__init__() # 부모 클래스 선언 및 초기화

        # 계정 정보
        self.SessionJson['AccountInfo'] = { 
            'iCloud ID' : ID, 
            'iCloud PW' : Password 
        }

        # 필수 헤더 정보 (인증 헤더 관련)
        self.SessionJson['AccountHeaders'] = {}

        # 필수 세션 정보 (WEB AUTH 관련)
        self.SessionJson['AccountSessions'] = {}
        
        self.First_Signin_Request(TrustToken) # 1차 인증 시작


    # 1차 인증 Request 함수
    def First_Signin_Request(self, TrustToken = ''):
        try:
            requestURL = "https://idmsa.apple.com/appleauth/auth/signin"

            header = {
                'Content-Type': 'application/json',
                'Referer': 'https://idmsa.apple.com/appleauth/auth/signin',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.1 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.1',
                'Origin': 'https://idmsa.apple.com',
                'X-Requested-With': 'XMLHttpRequest',
                'X-Apple-Widget-Key' : 'd39ba9916b7251055b22c7f910e2ea796ee65e98b2ddecea8f5dde8d9d1a815d'
            }

            data = {
                'accountName' : self.SessionJson['AccountInfo']['iCloud ID'],
                'password' : self.SessionJson['AccountInfo']['iCloud PW'],
                'rememberMe' : True,
                'trustTokens' : [TrustToken]
            }

            postData = json.dumps(data)
            response = requests.post(url=requestURL, headers=header, data=postData, proxies=proxies, verify=False)

            # 1차 인증 토큰 수집
            self.SessionJson['AccountHeaders']['scnt'] = response.headers['scnt']
            self.SessionJson['AccountHeaders']['X-Apple-Auth-Attributes'] = response.headers['X-Apple-Auth-Attributes']
            self.SessionJson['AccountHeaders']['X-Apple-Widget-Key'] = 'd39ba9916b7251055b22c7f910e2ea796ee65e98b2ddecea8f5dde8d9d1a815d'
            self.SessionJson['AccountHeaders']['X-Apple-Session-Token'] = response.headers['X-Apple-Session-Token']
            self.SessionJson['AccountHeaders']['X-Apple-ID-Account-Country'] = response.headers['X-Apple-ID-Account-Country']
            self.SessionJson['AccountHeaders']['X-Apple-ID-Session-Id'] = response.headers['X-Apple-ID-Session-Id']
            # self.SessionJson['AccountHeaders']['X-Apple-TwoSV-Trust-Eligible'] = response.headers['X-Apple-TwoSV-Trust-Eligible']
            

            # 2차 인증 여부 반환 (TrustToken이 존재하지 않거나 잘못 입력한 경우, 2차 인증 필요)
            if response.headers.get('X-Apple-TwoSV-Trust-Eligible') != None: # 2차 인증이 필요할 경우, 해당 키에 대한 값이 true로 존재함
                self.Second_Securitycode_Request() # 2차 인증을 통해 세션 갱신
                self.Get_TrustToken_Request() # trustToken 수집
                self.AccountLogin_Request() # WEB AUTH, PCS 쿠키 수집

            else:
                self.SessionJson['AccountHeaders']['X-Apple-TwoSV-Trust-Token'] = TrustToken
                self.AccountLogin_Request() # WEB AUTH, PCS 쿠키 수집
        
        except requests.exceptions.RequestException as e:
            print("1차 인증 Signin Request 실패", e)
        

    # 2차 인증 Request 함수
    def Second_Securitycode_Request(self):
        try:
            requestURL = "https://idmsa.apple.com/appleauth/auth/verify/trusteddevice/securitycode"

            header = {
                'Content-Type' : 'application/json',
                'Referer' : 'https://idmsa.apple.com/',
                'scnt' : self.SessionJson['AccountHeaders']['scnt'],
                'X-Apple-ID-Session-Id' : self.SessionJson['AccountHeaders']['X-Apple-ID-Session-Id'],
                'X-Apple-Widget-Key' : self.SessionJson['AccountHeaders']['X-Apple-Widget-Key'],
            }

            data = {
                'securityCode' : {
                    'code' : input(colored("Security Code(6-digit): ", 'yellow'))
                }
            }

            postData = json.dumps(data)

            # 리다이렉트를 허용하면 토큰 값을 받아올 수 없음
            response = requests.post(url=requestURL, headers=header, data=postData, proxies=proxies, verify=False, allow_redirects=False)

            # 2차 인증 후, X-Apple-Session-Token이 갱신됨
            self.SessionJson['AccountHeaders']['X-Apple-Session-Token'] = response.headers['X-Apple-Session-Token']

        except requests.exceptions.RequestException as e:
            print("2차 인증 Securitycode Reqeust 실패", e)


    # trustToken 수집 함수
    def Get_TrustToken_Request(self):
        try:
            requestURL = "https://idmsa.apple.com/appleauth/auth/2sv/trust"

            header = {
                'Content-Type' : 'application/json',
                'Referer' : 'https://idmsa.apple.com/',
                'scnt' : self.SessionJson['AccountHeaders']['scnt'],
                'X-Apple-ID-Session-Id' : self.SessionJson['AccountHeaders']['X-Apple-ID-Session-Id'],
                'X-Apple-Widget-Key' : self.SessionJson['AccountHeaders']['X-Apple-Widget-Key'],
            }

            response = requests.get(url=requestURL, headers=header, proxies=proxies, verify=False)


            # trusToken 및 갱신된 세션 수집
            self.SessionJson['AccountHeaders']['X-Apple-Session-Token'] = response.headers['X-Apple-Session-Token'] # X-Apple-Session-Token
            self.SessionJson['AccountHeaders']['X-Apple-TwoSV-Trust-Token'] = response.headers['X-Apple-TwoSV-Trust-Token'] # trustToken 수집

        except requests.exceptions.RequestException as e:
            print("TrustToken Reqeust 실패", e)


    # PCS, WEB AUTH 관련 쿠키 수집 함수
    def AccountLogin_Request(self):

        try:
            requestURL = "https://setup.iCloud.com/setup/ws/1/accountLogin"

            header = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language' : 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.1 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.1',
                'Referer' : 'https://www.icloud.com/',
                'Origin': 'https://www.icloud.com',
                'Connection': 'keep-alive',
            }

            data = {
                'dsWebAuthToken' : self.SessionJson['AccountHeaders']['X-Apple-Session-Token'],
                'accountCountryCode' : self.SessionJson['AccountHeaders']['X-Apple-ID-Account-Country'],
                'extended_login' : "true"
            }

            postData = json.dumps(data)
            response = requests.post(url=requestURL, headers=header, data=postData, proxies=proxies, verify=False)
            

            # 2차 인증 후에 쿠키 수집
            for cookie in response.cookies:
                self.SessionJson['AccountSessions'][cookie.name] = cookie.value

            # 개인정보 수집
            responseJson = json.loads(response.text)
            self.SessionJson['AccountInfo']['User Name'] = responseJson['dsInfo']['fullName']
            self.SessionJson['AccountInfo']['Dsid'] = responseJson['dsInfo']['dsid']
            self.SessionJson['AccountInfo']['Country Code'] = responseJson['dsInfo']['countryCode']
            self.SessionJson['AccountInfo']['Time Zone'] = responseJson['requestInfo']['timeZone']

        except requests.exceptions.RequestException as e:
            print("인증 쿠키 수집 AccountLogin Reqeust 실패", e)