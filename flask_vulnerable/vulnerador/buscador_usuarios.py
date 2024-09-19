from http import HTTPStatus
from random import randint as ri
import requests


"""
Usando información que conocemos de la empresa (por ejemplo que los nombres de usuario son 'usuario_NUMERO')
podemos realizar un ataque de enumeración
en el servidor para listar datos del server.
En este ejemplo, creamos usuarios aleatorios sin guardar información de los usernames.
Usando el ataque de enumeración, los obtendremos.
"""
SERVER_URL="http://localhost:5000"

def crear_usuarios_aleatorios(n: int):
    count = 0
    print("Creando usuarios aleatorios")
    for i in range(n):
        res = requests.post(f'{SERVER_URL}/usuarios/usuario_{ri(1, 1000)}')
        if res.ok:
            count += 1
            print("\tUsuario creado")
    print(f"usuarios creados: {count}")
    
def mapear_usuarios():
    usuarios_mapeados = []
    for i in range(1, 1001):
        usuario = f'usuario_{i}'
        # Pregunto si el server existe
        res = requests.get(f'{SERVER_URL}/usuarios/{usuario}')
        match res.status_code:
            # si encontre al usuario lo listo
            case HTTPStatus.OK:
                usuarios_mapeados.append(usuario)
                print(f"\tusuario encontrado: '{usuario}'")
            # si no existe sigo de largo
            case HTTPStatus.NOT_FOUND:
                continue
            case _:
                continue
    # imprimo los usuarios que se mapearon
    print("Usuarios mapeados:")   
    for i, usuario in enumerate(usuarios_mapeados):
        print(f"\t{i+1}. {usuario}")


# primero creo n usuarios de los que no guardo el nombre
crear_usuarios_aleatorios(10)

# usando un ataque por enumeración, encuentro los usuarios que se crearon
mapear_usuarios()