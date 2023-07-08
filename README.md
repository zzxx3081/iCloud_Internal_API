# iCloud Internal API Parser
## iCloud breaker (김재욱) [![](https://img.shields.io/badge/Kim_Jaeuk-220052?style=&logo=github&logoColor=white)](https://github.com/zzxx3081)

:herb: `iCloud breaker`는 iCloud Drive와 iCloud Mail 서비스를 분석하는 포렌식 도구입니다. iCloud breaker에 특정 사용자의 계정 정보를 입력하면, Internal API를 통해 해당 계정의 권한을 획득하고, 이를 통해 iCloud Drive와 iCloud Mail 서비스에 접근하여 관련 데이터를 자동적으로 수집할 수 있습니다.
iCloud breaker를 통해 iCloud Drive에 업로드된 파일들의 메타데이터를 확보하거나 특정 파일을 다운로드할 수 있습니다. 또한 iCloud Mail을 통해 주고 받은 메일 내역을 확인해볼 수 있고, 타임라인을 구축해볼 수도 있습니다.
iCloud breaker는 원격지 위법 데이터를 수집하는 포렌식 수사 관점에서 강점을 발휘합니다.

## How to Install iCloud breaker
:herb: iCloud breaker 설치방법은 소스코드(iCloud_Drive.py, iCloud_Login.py, iCloud_Mail.py, iCloud_Session.py, main.py) 및 패키지 파일(requirements.txt)을 모두 로컬 디렉토리에 다운로드한 후, 관련 패키지를 설치해주면 됩니다.

:herb: 패키지 설치 명령어
```python
pip install -r requirements.txt
```

## How to Start iCloud breaker
:herb: iCloud breaker 소스코드를 모두 다운로드 받은 후, 관련 패키지 설치가 완료되면 아래 명령어를 통해 도구를 실행할 수 있습니다.

:herb: 도구 시작 명령어
```python
python main.py
```


## Authentication

### Main Page
<p align="center"><img src="https://github.com/jpark-classroom/aiotforensics-zzxx3081/assets/74658309/03c0bd62-6534-4223-9430-8d86cfbe3d83"></p>

:herb: iCloud breaker는 2가지 옵션을 통해 iCloud 계정에 로그인할 수 있습니다. 1번 옵션은 미리 저장된 세션파일을 읽어 인증하는 방법입니다. iCloud는 로그인에 성공하면 서버에서 인증 세션을 발급해줍니다. 해당 세션의 유효기간은 30일이기 때문에 세션 정보를 파일로 저장해두고 재사용이 가능합니다. iCloud breaker의 2번 옵션을 통해 얻은 세션 정보를 파일로 저장해두면, 1번 옵션으로 간단하게 인증이 가능합니다.

<p align="center"><img src="https://github.com/jpark-classroom/aiotforensics-zzxx3081/assets/74658309/e60c4910-11b5-428c-84b8-631dbd862b2a"></p>

:herb: iCloud breaker의 2번 옵션은 1차 인증 및 2차 인증을 통해 서버에 직접 요청하여 세션 정보를 받아오는 방법입니다. 1차 인증은 ID, PW를 입력하는 절차로 구성되어 있으며 2차 인증은 iCloud에 연동된 디바이스로 전송된 숫자코드 6자리를 입력해야 인증이 완료됩니다. 한편, 브라우저 신뢰토큰이 있다면 2차 인증 없이 1차 인증만으로도 로그인이 가능합니다. 신뢰 토큰은 2차 인증을 완료했을 때 선택적으로 발급받을 수 있습니다. 아래 그림은 iCloud 브라우저의 1차 인증, 2차 인증, 브라우저 신뢰 화면을 나타냅니다.


### Authentication Example
#### :herb: iCloud breaker에서 1차 인증 및 2차 인증을 진행하는 화면 예시입니다.

<p align="center"><img src="https://github.com/jpark-classroom/aiotforensics-zzxx3081/assets/74658309/9f89573d-bb14-4c4f-9ffb-da443d690a9c"></p>

#### :herb: iCloud breaker에서 1차 인증 및 신뢰 토큰을 이용해 2차 인증을 우회하는 화면 예시입니다.

<p align="center"><img src="https://github.com/jpark-classroom/aiotforensics-zzxx3081/assets/74658309/26a7e931-510f-4a96-bc43-86134d743e92"></p>

#### :herb: iCloud 세션 파일을 저장하는 화면 예시입니다. 해당 파일은 Json 형식으로 되어 있습니다.

<p align="center"><img src="https://github.com/jpark-classroom/aiotforensics-zzxx3081/assets/74658309/b5983514-d86f-4008-a9a5-d47865156491"></p>

### iCloud Drive Menu

#### :herb: iCloud Drive Menu입니다. 메타데이터 추출, 다운로드 등 여러 기능들을 사용할 수 있습니다.

<p align="center"><img src="https://github.com/jpark-classroom/aiotforensics-zzxx3081/assets/74658309/3d3d6d35-5825-448a-8142-5fccdc5ca012"></p>


### iCloud Mail Menu

#### :herb: iCloud Mail Menu입니다. 메일 정보 추출, 원본 파일 다운로드 등 여러 기능들을 사용할 수 있습니다.

<p align="center"><img src="https://github.com/jpark-classroom/aiotforensics-zzxx3081/assets/74658309/780a72b4-4e08-450f-9b5e-fa57d1b3d3c8"></p>

