import requests
import re

DVWA_URL = "http://0.0.0.0"
LOGIN_URL = f"{DVWA_URL}/login.php"
COMMAND_INJECTION_URL = f"{DVWA_URL}/vulnerabilities/exec/"
BRUTE_FORCE_URL = f"{DVWA_URL}/vulnerabilities/brute/"
SLQ_INJECTION_URL = f"{DVWA_URL}/vulnerabilities/sqli/"
SLQ_INJECTION_BLIND_URL = f"{DVWA_URL}/vulnerabilities/sqli_blind/"

DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'password'

def generar_session(username:str=DEFAULT_USERNAME, password:str=DEFAULT_PASSWORD) -> requests.Session:
    """
        Genera una sesión para la pagina de DVWA, retorna la sesión cargada para realizar consultas.
    """
    session = requests.Session()
    login_page = session.get(LOGIN_URL)
    csrf_token = re.search(r"name='user_token' value='(.+?)'", login_page.text).group(1)

    login_data = {
        'username': username,
        'password': password,
        'Login': 'Login',
        'user_token': csrf_token
    }
    login_response = session.post(LOGIN_URL, data=login_data)
    if 'index.php' in login_response.url:
        print("Inicio de sesión exitoso")
    else:
        print("Error al iniciar sesión")
        exit()
    return session

def obtener_respuesta_dvwa(html_response: str | requests.Response) -> str|None:
    """
    Toma un html de un GET/POST de una consulta a dvwa y retorna solo la respuesta o None si no tiene response,
    """
    html_response = html_response if isinstance(html_response, str) else html_response.text
    
    # Las respuestas de las consultas en dvwa, vienen en un unico tag <pre> encapsulado.
    buscador = re.search('<pre>(.*)</pre>', html_response, flags=re.DOTALL)
    
    if (buscador):
        # Obtengo la respuesta del server
        resultado_comando = buscador.group(1)
        # quito <pre> y <br> de las consultas anidadas de dvwa
        resultado_comando = resultado_comando.replace('<br />', '\n')
        resultado_comando = resultado_comando.replace('<pre>', '\n')
        resultado_comando = resultado_comando.replace('</pre>', '\n')
        
        return resultado_comando
    
    return None