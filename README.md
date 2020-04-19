# Terminal Password Manager

## Description 

#### General 
This repository provides you a password manager in your terminal (mac OS). 
You can easily save your passwords but also IDs, mails or any remarks. 

All your passwords are protected with one general password that you will be asked to provide during the installation. You can improve the level of security of this password manager by moving to a flash drive a file named `.saveSalt` (created during the installation), needed to decode your data. If this file is moved on a flash drive, you will need to plug it in each time you want to use the password manager.

The file `.save.json` is used to save all your information and `.saveSalt` is used for the encryption. 

There are two different ways to retrieve a password : 

1) `get` : **Copies your password for 10 seconds in the clipboard** and displays the ID, the mail and the remark if there is one attached to this password. 
2) `see`: **Copies your password in the clipboard** and displays the ID, the mail, the *password* and the remark if there is one. 

All your passwords and their related information will be linked to a key. This key will be used to find the password when you will need it. 

#### Example of execution

![example](Example.png)

The research for the correct key is tolerent and the password manager will ask you to choose the correct key if several passwords match the research. 
All the options are listed in the **How to use it** section. 


## How to install 

* First clone this repository. 

* Then run the following command to install necessary packages.

```zsh
pip3 install cryptography
```

* Then go in the folder of the project and run this command to initialise your password manager. This will ask you a password that will be used to encode your future data. It will also create two files `.save.json` and `.saveSalt`. 
**Do not modify or lose those files, otherwise you will lose all your saved information** 

```zsh
python3 passw.py init
```

> If you want to move `.saveSalt` on a flash drive as mentioned in the description you will need to edit in `passw.py` the following constant : `saltFileName`. 
> For example : `saveFileName = /PATH/TO/.saveSalt` 

> For more safety you can also keep in a safe place a copy of `.saveSalt` 

* In order to be usable from the terminal, add this following lines in your `.bashrc` or `.zshrc` file. You need to write the path to this project in `"PATH/TO/PROJECT"` (can be found by running `pwd` in a terminal while in the project folder).

```zsh
# password manager shortcut
p (){
        DIR="`pwd`"
        builtin cd "/PATH/TO/PROJECT"
        case $1 in
                "add") python3 passw.py add          ;;
                "get") python3 passw.py get "$2"     ;;
                "see") python3 passw.py see "$2"     ;;
                "delete") python3 passw.py delete    ;;
                "edit") python3 passw.py edit        ;;
                *) echo "Unvalid argument"           ;;
        esac
        builtin cd $DIR
}
```

## How to use it

* To *add* a password run : 

```zsh 
p add
```

The first thing asked by this command is the key that will be used to retrieve your password. 

* To *delete* a password run : 

```zsh 
p delete
```

* To *edit* a password run :

```zsh 
p edit
```

* To *get* a password : 

```zsh 
p get <key>
```

* To *see* a password : 

```zsh 
p see <key>
```

For `get` and `see`, \<key\> represents the key linked to the password you're looking for. 
This \<key\> does not have to be exact, the password manager is tolerent and will ask you if several passwords match the research. 

> `p get ""` will list all the current keys that are registered in the password manager