from funciones import funciones as f
from flask import Flask, render_template, app, request, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.abspath("./uploads/")

# creando una base de flask
app = Flask(__name__)

# creando configuraciones de la app
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(["json"])

# carga e inicio
@app.route('/')
def home():
    return render_template('inicio.html')

#Pagina de nuestro proyecto
@app.route('/inicio/nuestroProyecto')
def nuestroProyecto():
    return render_template('nuestroProyecto.html')

# Del inicio a principal (donde estan las opciones, texto plano o json)
@app.route('/inicio/principal1')
def principal1():
    return render_template('principal1.html')

#Las secciones de academicos, usuarios de redes sociales, etc
@app.route('/principal1/secciones')
def secciones():
    return render_template('secciones.html')

# seccion mostrada al usuario de redes sociales y vulnerables donde se pide el archivo json y se procesa
@app.route('/principal1/secciones/principalGeneral', methods=["GET", "POST"])
def principalGeneral():
    if request.method == "POST":
        if "ourfile" not in request.files:
            return "el formulario no tiene el archivo"
        f = request.files["ourfile"]
        if f.filename == "":
             return render_template('noArchivo.html')
        if f and allowed_file(f.filename):
            filename = f.filename
            f.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            print ("Subida correcta: " + filename)
            return redirect( url_for("chat", archivo = filename) )
        else:
            return "archivo no valido!"

    return render_template('principalGeneral.html')

# revisa si la extension del archivo es valida
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS

# De principal1 (donde están las opciones), texto plano y json
@app.route('/principal1/principal', methods=["GET", "POST"])
def principal():
    if request.method == "POST":
        if "ourfile" not in request.files:
            return "el formulario no tiene el archivo"
        f = request.files["ourfile"]
        if f.filename == "":
            return render_template('noArchivo.html')
        if f and allowed_file(f.filename):
            filename = f.filename
            f.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            print ("Subida correcta: " + filename)
            return redirect( url_for("analisis", archivo = filename) )
        else:
            return "archivo no valido!"

    return render_template('principal.html')

# carga el archivo subido y lo muestra en el template
def get_file(filename):
    listaMensajes, listaUsuarios = f.cargarArchivo("uploads/" + filename)
    listaResultados = f.analizaConversacion(listaMensajes, listaUsuarios)
    f.hacerHTML(listaMensajes)
    return listaResultados

# De las opciones a la opcion de texto plano
@app.route('/inicio/principal1/plano')
def plano():
    return render_template('plano.html')

# De cargar archivo json a la muestra del analisis
@app.route('/principal/analisis/<archivo>', methods = ['GET'])
def analisis(archivo):

    if request.method == 'GET':
        resultados = get_file(archivo)
        # se mandaran al template los contenidos de la lista de resultados los cuales son:
        tm = resultados[0]
        ta = resultados[1]
        por = round(resultados[2], 2)
        uv = resultados[3]
        ua = resultados[4]
        return render_template('analisis.html', totalMensajes = tm, totalAgresiones = ta, porcentaje = por, usuarioVictima = uv, usuarioAgresor = ua)

# De la muestra del análisis al chat a los usuarios de redes sociales y vulnerables
@app.route('/chat/<archivo>', methods = ['GET', 'POST'])
def chat(archivo):
    if request.method == 'GET':
        resultados = get_file(archivo)
        return render_template('chat.html')

# Esta parte es la parte de la funcion del archivo de texto plano
@app.route('/principal1/plano', methods=['GET','POST'])
def predict():
    if request.method == 'POST':
        message = request.form['message']
        pred = f.analizaTexto(message)
        return render_template('plano.html', prediction=pred)
    else:
        return render_template('plano.html', prediction="No se pudo realizar la deteccion!")

# FUNCION QUE RECIBE EL CORREO PARA MANDAR PDF
@app.route('/enviado', methods=['POST'])
def PDF():

    #Recibimos el correo
    text = request.form['nombre']
    print(text)

    #Mandamos llamar la funcion para crear PDF
    f.conviertePDF()

    # mandamos llamar la funcion que envia la cadena recibida en el input
    f.enviaMail(text)
    
    return render_template('enviado.html')


if __name__ == '__main__':
    app.run()
