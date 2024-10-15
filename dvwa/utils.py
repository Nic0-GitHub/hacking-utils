import requests
import re

LOGIN_URL = "http://0.0.0.0/login.php"
COMMAND_INJECTION_URL = "http://0.0.0.0/vulnerabilities/exec/"
BRUTE_FORCE_URL = "http://0.0.0.0/vulnerabilities/brute/"
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
