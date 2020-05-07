import os
import time
import platform

time.sleep(10)
if (platform.system() == "Darwin"):
    os.system("echo | tr -d '\n' | pbcopy")
elif (platform.system() == "Linux"):
    os.system("echo | xclip -selection clipboard ")
