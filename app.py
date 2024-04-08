from usuario import Usuario
from usuarioobd import UsuarioOBD
from autenticador import Autenticador
from libro import Libro
from base_libros import BaseLibros
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, abort
import sqlite3
import os
import secrets
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.secret_key = 'secretalejandria123' 
conn = sqlite3.connect('base.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        pregunta_seguridad TEXT NOT NULL,
        respuesta_seguridad TEXT NOT NULL,
        ha_intercambiado BOOLEAN DEFAULT 0
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS libros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        autor TEXT, 
        clasificacion TEXT,
        archivo TEXT NOT NULL,
        token TEXT
    )
''')




conn.commit()
conn.close()
usuario_obd = UsuarioOBD()
autenticador = Autenticador()
base_libros = BaseLibros()
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        copassword = request.form['copassword']
        pregunta_seguridad = request.form['pregunta_seguridad']
        respuesta_seguridad = request.form['respuesta_seguridad']
        politica_privacidad = request.form['politica_privacidad']

        if not politica_privacidad:
            error = "Debes aceptar la politica de privacidad"
        elif password != copassword:
            error = "Las contraseñas no son las mismas"
        else:
           nuevo_usuario = Usuario(None, email, password, pregunta_seguridad, respuesta_seguridad, False )
           usuario_obd.guardar_usuario(nuevo_usuario)

           return redirect(url_for('index'))

    return render_template('registro.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        usuario = usuario_obd.buscar_por_email(email)

        if usuario and usuario.password == password:
            session['usuario_id'] = usuario.id
            session['email'] = email
            session['ha_intercambiado'] = usuario.ha_intercambiado
            
            return redirect(url_for('pagina_principal'))

    return render_template('index.html')

@app.route('/pagina_principal', methods=['GET', 'POST'])
def pagina_principal():
    autenticador.redirigir_si_no_autenticado()
    email = session['email']
    
    libros = base_libros.obtener_todos_los_libros()

    
    query = request.args.get('query', '')
    if query:
        libros = base_libros.buscar_libros(query)

    return render_template('pagina_principal.html', libros=libros)

    
@app.route('/recuperar', methods=['GET', 'POST'])
def recuperar():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        respuesta_seguridad = request.form['respuesta_seguridad']

        usuario = usuario_obd.buscar_por_email(email)

        if usuario and usuario.respuesta_seguridad == respuesta_seguridad:
            session['usuario_id'] = usuario.id
            return redirect(url_for('cambiar_contrasena'))
        else:
            error = "La respuesta no es correcta"


    return render_template('recuperar.html', error=error)

@app.route('/cambiar_contrasena', methods=['GET', 'POST'])
def cambiar_contrasena():
    error = None
    usuario_id = session.get('usuario_id')

    if not usuario_id:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        nueva_contrasena = request.form['nueva_contrasena']
        confirmar_contrasena = request.form['confirmar_contrasena']

        if nueva_contrasena != confirmar_contrasena:
            error = "Las contraseñas no coinciden"

        else:
            conn = sqlite3.connect('base.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET password = ? WHERE id = ?", (nueva_contrasena, usuario_id))
            conn.commit()
            conn.close()
            

            session.pop('usuario_id', None)
            return redirect(url_for('index'))
        
    return render_template('cambiar_contrasena.html', error=error)

@app.route('/intercambiar_libro', methods=['GET','POST'])
def intercambiar_libro():
    error = None
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        clasificacion = request.form['clasificacion']
        archivo = request.files['archivo']

        if archivo and allowed_file(archivo.filename):
            filename = secure_filename(archivo.filename)
            archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            token = secrets.token_hex(8)  

            nuevo_libro = Libro(titulo=titulo, autor=autor, clasificacion=clasificacion, archivo=filename, token=token)
            
        
            base_libros.guardar_libro(nuevo_libro)
            session['ha_intercambiado'] = True
            
            return render_template('intercambiar_libro.html', token=token)
            

        else:
            error = "Archivo no permitido"
    
    return render_template('intercambiar_libro.html', error=error)
        

@app.route('/buscar_libros', methods=['GET'])
def buscar_libros():
    query = request.args.get('query', '')
    libros = base_libros.buscar_libros(query)
    return render_template('resultado_busqueda.html', libros=libros, query=query)

@app.route('/descargar_libro/<token_descarga>', methods=['GET'])
def descargar_libro(token_descarga):
    archivo_nombre = base_libros.obtener_libro_por_token_descarga(token_descarga)
    if archivo_nombre:
        return send_from_directory(app.config['UPLOAD_FOLDER'], archivo_nombre)
    else:
        abort(404) 

@app.route('/validar_token_descarga/<token_descarga>', methods=['GET', 'POST'])
def validar_token_descarga(token_descarga):
    if request.method == 'POST':
        token_ingresado = request.form['token']
        
        if token_ingresado == token_descarga:  
            return redirect(url_for('descargar_libro', token_descarga=token_descarga))
        
        
        error = "Token incorrecto. Inténtalo de nuevo."
        return render_template('pagina_principal.html', libros=base_libros.obtener_todos_los_libros(), error=error)

    
    return render_template('pagina_principal.html', libros=base_libros.obtener_todos_los_libros())

@app.route('/biblioteca', methods=['GET','POST'])
def biblioteca():
    print('Valor de ha_intercambiado en la sesión:', session.get('ha_intercambiado'))
    if not session.get('ha_intercambiado'):
        return redirect(url_for('pagina_principal'))
    
    libros = base_libros.obtener_todos_los_libros()
    return render_template('biblioteca.html', libros=libros)

@app.route('/configuracion',methods=['GET','POST'])
def configuracion():
    return render_template('configuracion.html')

@app.route('/cerrar_sesion')
def cerrar_sesion():
    session.clear()
    return redirect(url_for('index'))


@app.route('/cambiar_correo', methods=['GET', 'POST'])
def cambiar_correo():
    error = None
    usuario_id = session.get('usuario_id')

    if not usuario_id:
        return redirect(url_for('index')) 

    if request.method == 'POST':
        nuevo_correo = request.form['nuevo_correo']

        
        
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET email = ? WHERE id = ?", (nuevo_correo, usuario_id))
        conn.commit()
        conn.close()
        

        return redirect(url_for('configuracion')) 
    
    return render_template('cambiar_correo.html', error=error)

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('message')
def handle_message(message):
    print("Received message: " + message)
    if message != "User connected!":
        send(message, broadcast=True)

@app.route('/chat')
def chat():
    return render_template("chat.html", email=session['email'])

@app.route('/politica', methods=['GET','POST'])
def politica():
    return render_template('politica.html')

if __name__ == '__main__':
    app.run(debug=True)
