import os
import sys
import iCloud_Login, iCloud_Mail
from pyfiglet import Figlet
from termcolor import colored

# iCloud breaker Main Intro


def Main_intro():
    os.system('cls')
    f = Figlet(font='big')
    print(colored(f.renderText('iCloud     breaker'), 'blue'))
    print(colored(" - Research on Data Acquisition and Analysis for iCloud Service", 'blue'))
    print(colored(" - Institute of Cyber Security & Privacy (ICSP)", 'blue'))
    print(colored(" - Digital Forensic Research Center", 'blue'))
    print(colored(" - Made By Jaeuk Kim (Assistant Researcher)\n", 'blue'))


# Get iCloud Session Data
def Get_iCloud_Authentication_Session():

    while True:
        print(colored("\n[iCloud Authentication Menu]", 'yellow'))
        print("Select the Method of iCloud Authentication! There are Two Authentication methods.")
        print("If you have Session Information File (Format: Json) on your Local Storage, you should select \"File Based Session Authentication\" (Number 1). ")
        print("Otherwise, you have to get a new Session Informaion through iCloud Account Management Server.")
        print("If you want to make the new Session, you can choose \"Login Based Session Authentication\" (Number 2).")
        print(colored(
            "[warning] Don't select the option that \"Login Based Session Authentication\" (Number 2) too often.", 'red'))
        print(colored(
            "[warning] Since \"iCloud Breaker\" use Internal API based Authentication Method, iCloud Account Management Server may detect it.", 'red'))
        print(colored(
            "[warning] That is, Your IP or Apple account can be blocked by Apple.\n\n", 'red'))

        print("#    0. EXIT                                     #")
        print("#    1. File Based Session Authentication        #")
        print("#    2. Login Based Session Authentication       #")
        print("#    3. Show Menu List Again                     #\n")

        Number = int(input(colored("Select Authentication Menu: ", 'yellow')))

        if Number == 0:
            print(colored("\n[Shut Down]", 'yellow'))
            sys.exit()

        elif Number == 1:
            print(colored("\n[File Based Session Authentication]", 'yellow'))
            return iCloud_Login.Authentication_FileToken()

        elif Number == 2:
            print(colored("\n[Login Based Session Authentication]", 'yellow'))
            return iCloud_Login.Authentication_NewToken()

        elif Number == 3:
            os.system('cls')
            continue

        else:
            print("[Invalid Number] Try Again!")


# main
if __name__ == "__main__":

    # Intro
    Main_intro()

    # Get User Account Session
    Account_Session = Get_iCloud_Authentication_Session()

    # iCloud Drive

    # iCloud Mail
    iCloud_Mail.Forensic(Account_Session)
