import subprocess
import time
import os
import signal

MINUTES_TO_REFRESH = 30

"""
Restarts spotify client at 30 minute intervals
"""

while True:
    pro = subprocess.Popen("spotify", stdout=subprocess.PIPE,
                           shell=True, preexec_fn=os.setsid)

#     time.sleep(MINUTES_TO_REFRESH * 60)
    time.sleep(5)
    # Send the signal to all the process groups
    os.killpg(os.getpgid(pro.pid), signal.SIGTERM)
