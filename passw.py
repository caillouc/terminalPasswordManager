from cryptography.fernet import InvalidToken
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import time
import getpass
import json
import base64
import sys


# Constant

idKey = "id"
mailKey = "email"
hintKey = "hint"
remarkKey = "remark"
saveFileName = "/Users/pierrecolson/caillou/.save.json"
saltFileName = "/Users/pierrecolson/caillou/.saveSalt"


# Helper


def loadSalt():
    """ Load the salt file from the flash drive """
    with open(saltFileName, "rb") as file:
        data = file.read()
    return data


def encrypt(data, encryptionKey):
    """ Encode the given data """
    key = getKey(encryptionKey, loadSalt())
    f = Fernet(key)
    return f.encrypt(data)


def decrypt(data, encryptionKey):
    """ Decode the given data """
    key = getKey(encryptionKey, loadSalt())
    f = Fernet(key)
    return f.decrypt(data)


def getKey(psd, salt):
    """ Generate the key with the salt and the password """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(psd))


def exist(location):
    """ Check if the file at location exist """
    return os.path.exists(location)


def loadSave():
    """ Load the data set from the save file """
    with open(saveFileName, "rb") as file:
        data = file.read()
    data = data.decode('utf8')
    dic = json.loads(data)
    return dic


def storeSave(data):
    """ Write the data in the save file """
    data = str(data).replace("'", '"').encode()
    with open(saveFileName, "wb") as file:
        file.write(data)


def askField(forHint):
    """ check if there is no invalid cahr in the entry """
    i = ['"']
    while '"' in i:
        if forHint:
            s = getpass.getpass()
        else:
            s = input()
        i = list(s)
        if '"' in i:
            print("  ***        Can't contain <\"> character      ***  ")
            print("  *** Re enter a value for this field please  ***  ")
        else:
            return s


def askPassword():
    """ Ask for the decode password """
    print("\n ** Enter the decoding password ** ")
    password = getpass.getpass()
    dic = loadSave()
    try:
        decrypt(dic["check"][hintKey].encode(), password.encode())
    except InvalidToken:
        print("\n   ****   Invalid Password   ****   ")
        sys.exit(0)
    return password


def getTolerentKey(searchKey, dic):
    """ Find all the keys that can fit to the one given by the user """
    ret = []
    for key in dic:
        key = key.replace("-", "")
        if searchKey.lower() == key.lower():
            return [key]
        elif searchKey in key:
            ret.append(key)
    return ret


# Initialisation

def init():
    """ Initialise save and salt file """
    if exist(saveFileName):
        print("   ****   Ther is already a save file (" + saveFileName + ") ****   ")
        sys.exit(0)
    if exist(saltFileName):
        print("   ****   Ther is already a salt file (" + saltFileName + ") ****   ")
        sys.exit(0)
    createSalt()
    passwordByte = initEncodingPassword().encode()
    check = {"check": {
        "id": "DO NOT REMOVE",
        "email": "",
        "hint": "",
        "remark": "only here to check password"
    }}
    check["check"][hintKey] = encrypt(
        "CheckingPassword".encode(), passwordByte).decode('utf8')
    with open(saveFileName, 'w') as file:
        file.write(str(check).replace("'", '"'))


def createSalt():
    """ Create the salt file """
    salt = os.urandom(32)
    with open(saltFileName, 'wb') as file:
        file.write(salt)


def initEncodingPassword():
    """ Ask the password to initialise encryption """
    password = ""
    checkPassword = "check"
    counter = 0
    while (password != checkPassword and counter < 3):
        if (counter != 0):
            print("\n  ***  The two password are different  ***  \n")
        print(" ** Enter an encoding password ** ")
        password = getpass.getpass()
        print("\n ** Type it again ** ")
        checkPassword = getpass.getpass()
        counter += 1
    if (password == checkPassword):
        return password
    else:
        print("   ****   To many tries ...   ****   ")
        sys.exit(0)


# ADD

def userAdd():
    """ Prepare to add new Password, and ask the user all infos """
    print("\n __ Enter the new key __")
    key = askField(False)
    if key == "check":
        print("   ****   Can't add a key named check   ****   ")
        sys.exit(0)
    print(" __ Enter an id for " + key + " __")
    id = askField(False)
    print(" __ Enter an email for " + key + " __")
    email = askField(False)
    print(" __ Enter the password for " + key + " __")
    hint = askField(True)
    print(" __ Enter a remark for " + key + " __")
    remark = askField(False)
    add(key, id, email, hint, remark)


def add(key, id, email, hint, remark):
    """ Add all infos in the dictionary """
    passwordByte = askPassword().encode()
    dic = loadSave()
    if key in dic:
        print("\n **       The key already exist       ** ")
        print(" ** Do you want to override it (y/n)? ** ")
        res = ""
        while res != "y" or res != "yes" or res != "no" or res != "n":
            res = input()
            if res == "y" or res == "yes":
                break
            elif res == "n" or res == "no":
                return
            elif res == "q":
                sys.exit(0)
            else:
                print("  ***  Invalid Choice (y/n) (q to quit)  ***  ")
    dic[key] = {idKey: id, mailKey: email,
                hintKey: encrypt(hint.encode(), passwordByte).decode('utf8'), remarkKey: remark}
    storeSave(dic)
    print("\n ** Successfully added ** ")


# Get


def userGet(key, displayHint):
    """ Read the key in the dictionary """
    dic = loadSave()
    possibleKey = getTolerentKey(key, dic)
    hintInfo = chooseKeyAndGetInfo(possibleKey, dic)
    passwordByte = askPassword().encode()
    hint = decrypt(hintInfo[0][hintKey].encode(),
                   passwordByte).decode('utf8')
    display(hintInfo[0], hintInfo[1], hint, displayHint)


def chooseKeyAndGetInfo(possibleKey, dic):
    """ Return all possible hintInfo and chosen key """
    if not possibleKey:
        print("   ****   This key does not exist   ****   ")
        sys.exit(0)
    if len(possibleKey) == 1:
        return (dic[possibleKey[0]], possibleKey[0])
    else:
        choice = -1
        print("\n --- There are multiple key that match the research --- ")
        print(" 0 - : To quit the programm")
        for index, elem in enumerate(possibleKey):
            print(" " + str(index+1) + " - : <" + str(elem)+">")
        while choice > len(possibleKey) or (choice < 0):
            try:
                choice = int(input())
            except ValueError:
                print("  ***  Invalid choice  ***  ")
            if (choice == 0):
                sys.exit(0)
            elif (int(choice) <= len(possibleKey) and (choice > 0)):
                return (dic[possibleKey[choice-1]],
                        possibleKey[choice-1])
            else:
                print("  ***  Enter a valid number  ***  ")


def display(info, key, hint, displayHint):
    """ Display all the info for a given key """
    print()
    if info[idKey]:
        print("  =>  The ID for " + str(key) + " is : " + info[idKey])
    if info[mailKey]:
        print("  =>  The mail for " + str(key) + " is : " + info[mailKey])
    if list(hint):
        if displayHint:
            print("  =>  The password for " + str(key) +
                  " is : " + hint)
        else:
            os.system("echo '%s' | tr -d '\n' | pbcopy" % hint)
            os.system("python3 cleanPaste.py &")
    if info[remarkKey]:
        print("  =>  The remark for " + str(key) + " is : " + info[remarkKey])


def userDelete():
    """ Allow the user to delete a key """
    print("\n __ Enter the key you want to delete __")
    key = askField(False)
    dic = loadSave()
    possibleKey = getTolerentKey(key, dic)
    hintInfo = chooseKeyAndGetInfo(possibleKey, dic)
    if hintInfo[1] == "check":
        print("   ****   Can't remove the check key   ****   ")
        sys.exit(0)
    passwordByte = askPassword().encode()
    hint = decrypt(hintInfo[0][hintKey].encode(),
                   passwordByte).decode('utf8')
    display(hintInfo[0], hintInfo[1], hint, True)
    print("\n ** To confirm the supression re-enter your password ** ")
    askPassword()
    del dic[hintInfo[1]]
    storeSave(dic)
    print("\n ** Successfully removed ** ")


# Edit

def userEdit():
    """ Allow the user to edit somme of a key """
    print("\n __ Enter the key you want to edit __")
    key = askField(False)
    dic = loadSave()
    possibleKey = getTolerentKey(key, dic)
    hintInfo = chooseKeyAndGetInfo(possibleKey, dic)
    if hintInfo[1] == "check":
        print("   ****   Can't edit the check key   ****   ")
        sys.exit(0)
    passwordByte = askPassword().encode()
    hint = decrypt(hintInfo[0][hintKey].encode(),
                   passwordByte).decode('utf8')
    display(hintInfo[0], hintInfo[1], hint, True)
    print("\n --- Which field do you want to edit ? --- ")
    print(" 0 - : To quit the programm")
    print(" 1 - : The ID")
    print(" 2 - : The mail address")
    print(" 3 - : The password")
    print(" 4 - : The remark")
    choice = -1
    while choice > 4 or choice < 0:
        try:
            choice = int(input())
        except ValueError:
            print("  ***     Invalid choice     ***  ")
        if (choice == 0):
            sys.exit(0)
        elif (int(choice) <= 4 and choice > 0):
            print(" ** Enter the new value ** ")
            if choice == 3:
                value = askField(True)
            else:
                value = askField(False)
        else:
            print("\n  ***  Enter a valid number  ***  ")
    if choice == 1:
        hintInfo[0][idKey] = value
    elif choice == 2:
        hintInfo[0][mailKey] = value
    elif choice == 3:
        hintInfo[0][hintKey] = encrypt(
            value.encode(), passwordByte).decode('utf8')
    elif choice == 4:
        hintInfo[0][remarkKey] = value
    dic[hintInfo[1]] = hintInfo[0]
    storeSave(dic)
    print("\n ** Successfully edited ** ")


# Main


def main():
    """ Main """
    if len(sys.argv) > 1:
        if sys.argv[1] == "init":
            init()
        elif not exist(saveFileName) or not exist(saltFileName):
            print("   ****   Can't find all needed files (save and salt)   ****   ")
            sys.exit(0)
        elif sys.argv[1] == "add":
            userAdd()
        elif sys.argv[1] == "get" or sys.argv[1] == "see":
            if len(sys.argv) != 3:
                print(
                    "   ****   Not the right number of argument (get key) or (see key)   ****   ")
                sys.exit(0)
            else:
                userGet(sys.argv[2], sys.argv[1] == "see")
        elif sys.argv[1] == "delete":
            userDelete()
        elif sys.argv[1] == "edit":
            userEdit()
        else:
            print(
                "   ****   Invalid argument try {init, add, get, see, or remove}   ****   ")
            sys.exit(0)
    else:
        print(
            "   ****   There is no argument ... try {init, add, get, see, or remove}   ****   ")
        sys.exit(0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Au revoir !!")
        sys.exit(0)
