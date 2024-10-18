"Ejecución OK";
import os
import subprocess

def create_orphan_process():
    if os.fork() > 0:
        return
    
    os.setsid()
    subprocess.Popen(["python3", "-m", "http.server", "8081"])


try:
    create_orphan_process()
except Exception as e:
    consola_interativa = str(e)