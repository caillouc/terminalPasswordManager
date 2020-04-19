import os
import time

time.sleep(10)
os.system("echo | tr -d '\n' | pbcopy")
