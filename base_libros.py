import sqlite3
from libro import Libro
from conexion_base import ConexionBase
from autenticador import Autenticador
from flask import session

class BaseLibros(ConexionBase):
    def __init__(self, db_name='base.db'):
        super().__init__(db_name)
        self.autenticador = Autenticador()

    def conectar(self):
        return sqlite3.connect(self.db_name)
    
    def guardar_libro(self, libro):
        usuario_id = session.get('usuario_id')
        
        
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO libros (titulo, autor, clasificacion, archivo, token) 
            VALUES (?, ?, ?, ?, ?)
        ''', (libro.titulo, libro.autor, libro.clasificacion, libro.archivo, libro.token))
        cursor.execute("UPDATE usuarios SET ha_intercambiado = ? WHERE id = ?", (True, usuario_id))
        conn.commit()

        conn.close()
        
    
    def obtener_todos_los_libros(self):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM libros')
        libros = cursor.fetchall()
        conn.close()
        return [Libro(libro[1], libro[2], libro[3], libro[4], libro[5]) for libro in libros]

        
    
    def buscar_libros(self, query):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM libros 
            WHERE titulo LIKE ? OR autor LIKE ? OR clasificacion LIKE ?
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        libros = cursor.fetchall()
        conn.close()
        return [Libro(libro[1], libro[2], libro[3], libro[4], libro[5]) for libro in libros]

    
    def obtener_libro_por_token_descarga(self, token_descarga):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute('SELECT archivo FROM libros WHERE token = ?', (token_descarga,))
        resultado = cursor.fetchone()
        conn.close()
        return resultado[0] if resultado else None
    
    
