import os
from constants import DB_PATH
from dataclasses import dataclass
import sqlite3

@dataclass
class Usuario:
    id:int
    nombre:str
    password:str
    
    
    
class Database:
    instance = None

    sql_crear_tabla_usuarios = """\
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            password TEXT NOT NULL
        );
    """
    sql_actualizar_usuario_password = """\
        UPDATE usuarios SET password=?
        WHERE id = ?;    
    """
    sql_borrar_registros_usuarios = """\
        DELETE FROM usuarios;
    """
    sql_borrar_tabla_usuarios = """\
        DROP TABLE IF EXISTS usuarios;
    """
    sql_crear_usuario = """\
        INSERT INTO usuarios (nombre, password) VALUES (?, ?);
    """
    sql_obtener_usuario = """\
        SELECT id, nombre, password FROM usuarios WHERE nombre = ? OR id = ?;
    """
    sql_obtener_usuarios = """\
        SELECT id, nombre, password FROM usuarios;
    """
    
    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(Database, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        if not hasattr(self, 'connection'):
            if not os.path.exists(DB_PATH):
                with open(DB_PATH, 'x') as file:
                    pass
            self.connection = sqlite3.connect(DB_PATH, check_same_thread=False)
            self.cursor = self.connection.cursor()
            self.crear_tabla()

    def crear_tabla(self):
        """Crea la tabla de usuarios si no existe."""
        self.cursor.execute(self.sql_crear_tabla_usuarios)
        self.connection.commit()

    def crear_usuario(self, usuario: Usuario):
        """Crea un usuario si el usuario no existe."""
        if (self.obtener_usuario(usuario.nombre)):
            raise ValueError("El usuario ya existe")
        self.cursor.execute(self.sql_crear_usuario, (usuario.nombre, usuario.password))
        self.connection.commit()
    
    def obtener_usuario(self, param_buscar: int | str) -> Usuario | None:
        """Obtiene un usuario por nombre. si es int busca como id, si es str busca por nombre de usuario"""
        match param_buscar:
            case int(param_buscar):
                nombre = ""
                id = param_buscar
            case str(param_buscar):
                nombre = param_buscar
                id = -1
            case _:
                raise TypeError("Tipo de dato invalido")
        self.cursor.execute(self.sql_obtener_usuario, (nombre, id))
        
        if (u:=self.cursor.fetchone()):
            id, nombre, password = u
            return Usuario(id, nombre, password)
        
        return None
    
    def actualizar_usuario(self, usuario: Usuario):
        """Actualiza al usuario pasado en la base de datos"""
        if not usuario.id:
            raise ValueError("No se puede actualizar un usuario con id nulo")
        self.cursor.execute(self.sql_actualizar_usuario_password, (usuario.password, usuario.id))
        self.connection.commit()
        
    def reiniciar_usuarios(self):
        """Borra la tabla de usuarios para empezar de 0"""
        self.cursor.execute(self.sql_borrar_tabla_usuarios)
        self.cursor.execute(self.sql_crear_tabla_usuarios)
        
        self.connection.commit()
        
    def obtener_usuarios(self) -> list[Usuario]:
        """Obtiene todos los usuarios de la base de datos."""
        self.cursor.execute(self.sql_obtener_usuarios)
        return [Usuario(*u) for u in self.cursor.fetchall()]

    def cerrar_conexion(self):
        """Cierra la conexión a la base de datos."""
        self.connection.close()
        

if __name__ == '__main__':
    db = Database()
