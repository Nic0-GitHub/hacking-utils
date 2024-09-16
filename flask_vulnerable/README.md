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