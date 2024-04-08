import sqlite3
from usuario import Usuario
from conexion_base import ConexionBase
class UsuarioOBD(ConexionBase):
    def __init__(self, db_name='base.db'):
       super().__init__(db_name)

    def conectar(self):
        return sqlite3.connect(self.db_name)
        
    def guardar_usuario(self,usuario):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO usuarios (email, password, pregunta_seguridad, respuesta_seguridad, ha_intercambiado) VALUES (?, ?, ?, ?, ?)',
                       (usuario.email, usuario.password, usuario.pregunta_seguridad, usuario.respuesta_seguridad, usuario.ha_intercambiado))
        conn.commit()
        conn.close()

    def buscar_por_email(self, email):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
        usuario_data = cursor.fetchone()
        conn.close()

        if usuario_data:
            usuario = Usuario(*usuario_data)
            return usuario
        else:
            return None
        
