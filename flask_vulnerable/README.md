# Flask vulnerable para practicas de ciberseguridad

## Requisitos Previos
Asegúrate de tener instalado lo siguiente en tu sistema:

- **Python 3.7 o superior**: Puedes descargarlo desde [python.org](https://www.python.org/downloads/).
- **pip**: El gestor de paquetes de Python, generalmente se instala junto con Python.
## Pasos para Ejecutar la Aplicación

1. **Clona el Repositorio**
   Abre una terminal y ejecuta el siguiente comando para clonar el repositorio:

   ```bash
   git clone https://github.com/Nic0-GitHub/hacking-flask_vulnerable
   ```
2. **Navega a la carpeta del proyecto**
    crea un entorno virtual para python
    ```bash
        python -m venv nombre_entorno_virtual
    ```
3. **Entra en el entorno virtual**
    para Windows:
    ```bash
        nombre_entorno_virtual\Scripts\activate
    ```
    para Linux:
    ```bash
        source nombre_entorno_virtual/bin/activate
    ```
4. **Instala las dependencias del proyecto**
    ```bash
        pip install -r requirements.txt
    ```
5. **Ejecuta la aplicación**
    ```bash
        python app.py
    ```

# Detalles
Esta Aplicación flask es una colección de vulnerabilidades detalladas paso a paso para su explotación, sigue en desarrollo  y mejora constante.
Tiene como objetivo hacer una demostración sobre como explotar errores de desarrollo para aquellos que quieren empezar en el mundo del hacking, ✨rompan el mundo y diviertanse✨.

#### Argumentos que acepta la aplicación
-`[-p|--port]`: Para cambiar el puerto donde corre la aplicación.
-`[-d|--debug]`: Para activar el modo debug de la aplicación.
-`[-H|--host]`: Para cambiar el host donde corre la aplicación.
-`[-n|--no-logs]`: Para evitar la escritura de logs de sistema.


## Vulnerabilidad de ejecución de código arbitrarío en `/calcular` con `exec()`

### Descripción
El código en el endpoint `/calcular` permite a los usuarios enviar un JSON con claves que contienen expresiones matemáticas o código Python para ser ejecutado. Esto se hace a través de la función `exec()` de Python, que ejecuta código arbitrario dentro del contexto del servidor.

#### Código vulnerable:

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
#### Ejemplo de ejecución maliciosa.

Usando el conocimiento de como funciona la vulnerabilidad, podemos usar `;` para
Seguir enviando instrucciones para ejecutar nuestro código arbitrario.
```json
    {
        "calculo1": "10 + 30",
        "directorios_en_home": "10;import os; directorios_en_home=os.listdir('/home')",
        "intento_de_ls": "__import__('os').system('ls')"
    }
```
#### Impacto
Maxima o critica, no existe una vulnerabilidad más grave para un sistema que la ejecución arbitraría de código.
Un atacante con conocimiento podría levantar puertos, borrar archivos, leer información, crear usuarios, cambiar configuraciones, ect.
En este caso, si bien usamos una simple muestra de impresión de contenido de directorios se debe tener en cuenta que esta vulnerabilidad da control total al atacante del servidor.
Jamas, nunca, bajo NINGUN CONCEPTO, se debe permitir la ejecución de código a personal no autorizado con o sin conocimiento técnico dentro del servidor.

#### Conclusión
- Considerar usar herramientas más seguras como `eval()`, librerías especializadas para esto como `ast`.
- Limitar las funciones que tiene permitido el usuario en caso de obligatoriamente requerir ejecución de código.
- Usar una maquina virtual para ejecutar el código y solo retornar la información si tiene un formato adecuado.
- Analizar estrategias para evitar procesamiento por parte del servidor.
- Restringir los usuarios que tienen permiso de utilizar esta funcionalidad a personal técnico y de confianza si es necesario usar ejecución arbitraría.

## Vulnerabilidad de ejecución de código arbitrarío en `/comentario` con registro de datos sensibles

### Descripción
El código en el endpoint `/comentario` registra directamente el contenido del mensaje enviado por el usuario en los logs. Esto puede exponer datos sensibles si se almacenan o envían a través del mensaje.

#### Código vulnerable:

```python
@app.route('/comentario', methods=['POST'])
def mensaje():
    if not request.is_json:
        abort(HTTPStatus.BAD_REQUEST)
    
    mensaje:str = request.json['mensaje']
    
    if mensaje.startswith('/'):
        res = f"Este mensaje no es valido: '{mensaje}'"
        # Vulnerabilidad aquí
        app.logger.info(res)
        return Response(res, HTTPStatus.BAD_REQUEST)
    
    res = f"Mensaje recibido '{mensaje}'"
    # Vulnerabilidad aquí
    app.logger.info(res) 
    return Response('Recibido!', HTTPStatus.OK)
```

#### Ejemplo de ejecución maliciosa.
Si un usuario envía un mensaje con datos sensibles como contraseñas, estos se registrarán directamente en los logs, exponiendo esa información a cualquier persona con acceso a los logs del servidor:

```json
    {
        "mensaje": "clave_vulnerable"
    }
```
#### Impacto
Un usuario sin privilegios puede acceder a información confidencial, esto es sumamente grave para algunos casos criticos,
esta vulnerabilidad se obviara por motivos didacticos para el resto de endpoints, pero NUNCA es buena idea poner en logs contraseñas o 
información sensible.

#### Conclusión
- En caso de necesitar algún registro es preferible algo como `se cargaron XX caracteres en un mensaje`, o clarificar eventos `se recibio un mensaje` pero nunca usar datos introducidos.
Los logs no deben tener información sensible salvo que se trate de DEBUG por motivos de resolución de errores.
- Considerar que los logs son para registrar eventos para su posterior correción, no guardan información solo eventos que pasaron.

## Vulnerabilidad de sobrecarga de input en `/comentario`  por falta de validación de tamaño de entrada.

### Descripción
El código en el endpoint /comentario no verifica el tamaño de la entrada proporcionada por el usuario. Esto permite a un atacante enviar mensajes extremadamente grandes, lo que podría agotar el espacio en disco o los recursos del servidor, resultando en una denegación de servicio (DoS).


```python
@app.route('/comentario', methods=['POST'])
def mensaje():
    if not request.is_json:
        abort(HTTPStatus.BAD_REQUEST)
    
    mensaje:str = request.json['mensaje']
    
    # No se verifica el tamaño del mensaje
    res = f"Mensaje recibido '{mensaje}'"
    app.logger.info(res)
    return Response('Recibido!', HTTPStatus.OK)
```

#### Ejemplo de explotación
Un atacante podría enviar un mensaje muy grande repetidamente para llenar el espacio en disco:

```json
    {
        "mensaje": "ABC" * 10000000  # Mensaje de 10MB
    }
```
#### Impacto

Podría saturar la red produciendo un ataque de denegación de servicios como tambien podría dejar inutilizable al servidor por tiempo indefinido hasta que un administrador borre los mensajes maliciosos.
En caso de tener dispositivos de lectura/escritura lentas, podría ocasionar que otros sistemas dentro del mismo servidor se vean bloqueados para guardar archivos incluso habiendo espacio
disponible.

#### Conclusión
- Se debe considerar maximos de tamaños para cada usuario antes de considerar guardar su información en el servidor.
- Se puede rechazar los inputs mayores que cierto tamaño.


## Vulnerabilidad de introducción de código arbitrarío en  `/comentario`

### Descripción
Al no validar el tipo de contenido en el mensaje se permite la introducción de código dentro del servidor, lo que permite cargar todo tipo de contenido, incluyendo caracteres no imprimibles o código

#### Ejemplo de explotación
```json
    {
        "mensaje": "ls /home;" # código introducido sin validación
    }
```

#### Impacto
En caso de que no se hagan validaciones en otra parte del sistema al validar los mensajes, puede producirse ejecución de código arbitraria en otros lugares.
Puede que se introduzcan datos no imprimibles que produzcan errores al intentar renderizar la información.

#### Conclusión
- Analizar sintacticamente el input de los usuarios.
- Quitar caracteres no imprimibles
- Considerar rechazar contenido que contenga caracteres usados en código (';', '&', '|', '@')
- Registrar siempre el contenido de este endpoint antes de usarlo o renderizarlo.



## Vulnerabilidad de ejecución de código arbitrarío en `/usuarios/<usuario>` por Enumeración de Usuarios

### Descripción

El código en el endpoint `/usuarios/<usuario>` permite consultar y crear usuarios. Sin embargo, cuando se solicita un nombre de usuario inexistente, el servidor responde de manera diferente si el usuario existe o no, lo que habilita un ataque de **enumeración de usuarios**. Esto permite a un atacante verificar la existencia de usuarios y recolectar información sobre los mismos, explotando el comportamiento del servidor ante solicitudes HTTP.

#### Código vulnerable:

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
#### Ejemplo de explotación: `buscador_usuarios.py`
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

#### Impacto
Este tipo de vulnerabilidad permite a un atacante descubrir usuarios válidos en el sistema, lo cual es un punto de partida para ataques más avanzados, como fuerza bruta o spear phishing. La respuesta del servidor debería ser uniforme tanto para usuarios existentes como no existentes para evitar esta fuga de información.
Es de grave consideración que la obtención de este tipo de información NO es ilegal para la mayoria de casos, es decir, se considera que este tipo de información es "publica" puesto que
cualquier usuario/internauta puede acceder a ella desde cualquier lugar sin necesidad de autenticación o validación adicional por lo que los atacantes tienen un agujero legal para obtener 
información de la organización.

#### Conclusión
- Responder de forma generica para multiples resultados(USUARIO_NOT_FOUND, DATA_FORBIDDEN)
- Redirigir el trafico a la pagina de inicio de sesión.
- Limitar las consultas que un ip puede hacer en el día para limitar la potencia del ataque.
- No usar reglas genericas para la creación de usuarios para dificultar el listado.

## Vulnerabilidad de generación insegura de contraseñas en `/usuarios/<usuario>` POST

### Descripción
Se aprovecha de la generación de valores pseudoaleatoriso con random para encontrar la semilla que genero las contraseñas
y generar un listado de contraseñas posibles.

#### Código vulnerable:
```python
@app.route('/usuarios/<usuario>', methods=['GET', 'POST'])
def pagina_usuario(usuario):
    get_nombre = lambda u: u.get('nombre', '')
    match request.method:
        case 'GET':
            # Vulneralibilidad de ataque de enumeración
            if usuario in map(get_nombre, usuarios):
                app.logger.info(f"Se accedio a la pagina del usuario: {usuario}")
                return Response(f"<h1>Hola, {usuario}</h1>")
            return Response("<h1>usuario no encontrado</h1>",HTTPStatus.NOT_FOUND)
        case 'POST':
            import string
            if usuario in map(get_nombre, usuarios):
                return Response("<h1>usuario invalido</h1>", HTTPStatus.CONFLICT)
            valid_chars = string.ascii_letters + string.digits
            # Vulnerabilidad de generación insegura con seed
            d = {
                "nombre": usuario,
                "password": ''.join(generador.choices(valid_chars, k=15))
            }
            
            app.logger.info(f"Se creo un nuevo usuario: {usuario}")
            usuarios.append(d)
            
            return jsonify(d), HTTPStatus.CREATED
```

#### Ejemplo de explotación: `buscador_passwords.py`
Usando asumiciones intenta inferir la seed usada para mostrar contraseñas usadas para la creación de contraseñas en el sistema.


#### Impacto
Critico, si un atacante puede obtener la seed de generación de contraseñas podría acceder a todos los usuarios que el sistema genera
incluyendo los que aún no han sido creados.
Cabe aclarar que es muy difícil de romper si se esta bien configurado y que puede llegar a requerir enormes capacidades de computo 
pero resulta una forma efectiva de obtener control de un sistema de forma sencilla.
Una vez encontrada la seed, TODAS las contraseñas seran vulneradas independientemente del largo de la contraseña generada.

#### Conclusión
- Para la generación de contraseñas es preferible librerías como `secrets` antes que random.
- El largo de las contraseñas generadas tambien podría ser variable para complicar el hallazgo de la seed.
- A la hora de usar una seed con random se puede usar una seed de muchos digitos (15 - 20) para evitar la deducción por fuerza bruta.
- Se puede escojer entre más de un generador (seleccionar uno en base a un numero aleatorio), para que incluso si se encontrara 1,
solo una pequeña parte de los usuarios sería vulnerada.