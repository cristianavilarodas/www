from flask import Flask, render_template, jsonify, request, redirect, session
import mysql.connector
import os
import shutil
from werkzeug.utils import secure_filename

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="amoress123",
    database="prueba1",
)

myCursor = mydb.cursor()

app = Flask(__name__)
app.secret_key = 'mi_clave_secreta'


@app.route('/usuarioPaginaInicio')
def inicio2():
    return render_template('inicioUsuario.html')


@app.route('/')
def inicioLoginRegistrar():
    return render_template('inicioLoginRegistro.html')


@app.route('/paginaCanciones')
def canciones():
    query = "SELECT * FROM canciones"
    myCursor.execute(query)
    datos = myCursor.fetchall()
    return render_template("canciones.html", listaCanciones=datos)


@app.route('/perfilPagina')
def perfil():
    # Obtener el ID del usuario que ha iniciado sesión
    user_id = session.get('user_id')

    if user_id:
        # Consultar los datos del usuario utilizando su ID
        query = "SELECT usuario, correo, contraseña FROM usuario WHERE idusuario = %s"
        values = (user_id,)
        myCursor.execute(query, values)
        result = myCursor.fetchone()

        if result:
            # Obtener los datos del usuario
            usuario = result[0]
            correo = result[1]
            contraseña = result[2]
        else:
            # Manejo del caso si no se encuentra el usuario
            usuario = ""
            correo = ""
            contraseña = ""

        # Obtener la lista de canciones desde la base de datos
        query = "SELECT * FROM canciones"
        myCursor.execute(query)
        datos = myCursor.fetchall()

        return render_template('perfil.html', usuario=usuario, correo=correo, contraseña=contraseña, listaCanciones=datos)

    # Si no hay sesión activa o no se encuentra el usuario en la base de datos, redirigir a la página de inicio de sesión
    return redirect('/')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Consultar la base de datos para verificar las credenciales
    query = "SELECT * FROM usuario WHERE usuario = %s AND contraseña = %s"
    values = (username, password)
    myCursor.execute(query, values)
    result = myCursor.fetchone()

    if result:
        # Obtener el ID del usuario
        user_id = result[0]

        # Guardar el ID del usuario en la sesión
        session['user_id'] = user_id

        # Las credenciales son correctas, puedes redireccionar a la página correspondiente
        return redirect('/usuarioPaginaInicio')
    else:
        # Las credenciales son incorrectas, puedes mostrar un mensaje de error
        return redirect('/')


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    # Insertar los datos en la tabla usuario
    query = "INSERT INTO usuario (usuario, correo, contraseña) VALUES (%s, %s, %s)"
    values = (username, email, password)
    myCursor.execute(query, values)
    mydb.commit()

    # Puedes redireccionar a la página correspondiente después del registro exitoso
    return redirect('/')


@app.route('/upload-song', methods=['POST'])
def upload_song():
    song_name = request.form['songName']
    artist_name = request.form['artistName']
    song_file = request.files['songFile']
    genre = request.form['genre']
    filename = secure_filename(song_file.filename)

    song_file.save('C:/Users/khukhukjkj/Documents/9 semestre/www/proyectos/proyecto final/static/canciones/' + filename)

    # Obtener el último ID insertado en la tabla
    query = "SELECT MAX(idcanciones) FROM canciones"
    myCursor.execute(query)
    last_id = myCursor.fetchone()[0]

    # Generar un nuevo ID incrementando el último ID en 1
    new_id = last_id + 1

    # Insertar la canción con el nuevo ID
    query = "INSERT INTO canciones (idcanciones, nombre, artista, genero) VALUES (%s, %s, %s, %s)"
    values = (new_id, song_name, artist_name, genre)
    myCursor.execute(query, values)
    mydb.commit()

    return redirect('/paginaCanciones')


@app.route('/borrar_cancion', methods=['POST'])
def borrar_cancion():
    cancion_id = request.form.get('cancionID')

    # Consultar el nombre del archivo de la canción en la base de datos
    query = "SELECT nombre FROM canciones WHERE idcanciones = %s"
    values = (cancion_id,)
    myCursor.execute(query, values)
    result = myCursor.fetchone()
    if result:
        nombre_archivo = result[0] + ".mp3"

        # Eliminar el archivo de la canción del sistema de archivos
        ruta_archivo = os.path.join('static', 'canciones', nombre_archivo)
        ruta_completa = os.path.abspath(ruta_archivo)
        if os.path.exists(ruta_completa):
            os.remove(ruta_completa)
        else:
            print(f"No se encontró el archivo: {ruta_completa}")

        # Eliminar la canción de la base de datos
        query = "DELETE FROM canciones WHERE idcanciones = %s"
        values = (cancion_id,)
        myCursor.execute(query, values)
        mydb.commit()

    # Después de borrar la canción, puedes redirigir a la página de lista de canciones
    return redirect('/paginaCanciones')


if __name__ == "__main__":
    app.run(debug=True)




