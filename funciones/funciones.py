# funcion que carga el archivo y lee el contenido
def cargarArchivo(ruta):
    import json
    import datetime

    # creando clases para crear objetos de tipo usuario y mensaje
    class usuario:
        def __init__(self):
            self.nombre = ""
            self.totalAgresiones = 0

    class message:
        def __init__(self):
            self.usuario = ""
            self.mensaje = ""
            self.tiempo = ""
            self.agresividad = 0

    # listas para guardar los mensajes y los usuarios
    listaMensajes = []
    listaUsuarios = []

    with open(ruta) as contenido:
        conversacion = json.loads(contenido.read())

        # leyendo los nombres de los usuarios del chat
        for user in conversacion["participants"]:
            u = usuario()
            u.nombre = user.get("name", "")
            listaUsuarios.append(u)

        # leyendo los mensajes de la conversacion
        for mensaje in conversacion["messages"]:
            conv = message()
            conv.usuario = mensaje.get("sender_name", "")
            conv.mensaje = mensaje.get("content", "")

            milisegundos = mensaje.get("timestamp_ms")
            date = datetime.datetime.fromtimestamp(milisegundos/1000.0)
            date = date.strftime('%Y-%m-%d %H:%M:%S')

            conv.tiempo = date

            if conv.mensaje == "":
                pass
            else:
                listaMensajes.append(conv)

    contenido.close()
    return listaMensajes, listaUsuarios

# funcion que lee la lista de mensajes dada por cargarArchivo y lo convierte en html
def hacerHTML(listaMensajes):
    listaHTML = []

    for mensaje in listaMensajes:
        agresividad = str(mensaje.agresividad)
        parrafo =   f"<div class = '{agresividad}' >\n" + f"\t<p>{mensaje.usuario}</p>\n" + f"\t<p>{mensaje.mensaje}</p>\n" + f"\t<p>{mensaje.tiempo}</p>\n" + "</div>\n"

        listaHTML.append(parrafo)

    nuevoArchivo = open("templates/nuevo.html", "w")
    nuevoArchivo.writelines(listaHTML)
    nuevoArchivo.close()

# funcion que analiza cada mensaje de la lista de mensajes y comprueba si es o no agresiva
def analizaConversacion(listaMensajes, listaUsuarios):
    from sklearn.base import ClassifierMixin
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import PassiveAggressiveClassifier
    import pandas as pd
    from sklearn.model_selection import train_test_split

    #bolsa de palabras en forma de vector de tamaño de 3000 
    tfvect = TfidfVectorizer(max_features=3000)

    # se carga el archivo .csv
    dataframe = pd.read_csv('train_aggressiveness.csv')
    x = dataframe['Text']
    y = dataframe['Category']

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)

    tfid_x_train = tfvect.fit_transform(x_train)
    tfid_x_test = tfvect.transform(x_test)
    print(f"Vocabulario total: {len(tfvect.vocabulary_)} palabras")

    #creamos un objeto de la clase PassiveAggressiveClassifier
    classifier = PassiveAggressiveClassifier(max_iter=50)
    tfid_x_train = tfvect.fit_transform(x_train)
    tfid_x_test = tfvect.transform(x_test)

    #La funcion fit del objeto TfidfVectorizer aprende el vocabulario y idf del conjunto de entrenamiento dado
    classifier.fit(tfid_x_train,y_train)

    # Analizando la lista de mensajes
    for m in listaMensajes:
        men = m.mensaje
        input_data = [men]
        #vectorizamos el texto
        vectorized_input_data = tfvect.transform(input_data)
        
        #Hacemos le prediccion mediante el texto ya vectorizado
        prediction = classifier.predict(vectorized_input_data)
    
        #imprimos la matriz vectorizada
        print(vectorized_input_data)
        
        _, col_index = vectorized_input_data.nonzero()
        
        #Total de palabras
        print(f"Palabras totales que se tomaron de referencia: {len(col_index)}")
                
        #Imprimomos las plabras
        for i in col_index:
            print(sorted(list(tfvect.vocabulary_))[i])

        if prediction[0] == 1:
            m.agresividad = "agresiva"

            # se busca en la lista de usuarios por el agresor
            for u in listaUsuarios:
                if u.nombre == m.usuario:
                    u.totalAgresiones += 1
        else:
            m.agresividad = "noAgresiva"

    # se declaran los datos que contendran el resultado del analisis
    totalMensajes = len(listaMensajes)
    
    # se busca por la cantidad de mensajes agresivos
    totalAgresiones = 0
    for m in listaMensajes:
        if m.agresividad == "agresiva":
            totalAgresiones += 1
    
    # se saca el porcentaje de las cifras obtenidas
    porcentaje = (totalAgresiones * 100) / totalMensajes

    # se obtiene que usuario tuvo mas agresiones en la conversacion
    usuarioAgresor = ""
    usuarioVictima = ""
    aux = 0
    for u in listaUsuarios:
        
        if u.totalAgresiones > aux:
            aux = u.totalAgresiones
            usuarioAgresor = u.nombre
        else:
            aux = u.totalAgresiones
            usuarioVictima = u.nombre

    # se crea una lista con los resultados
    resultados = []
    resultados.append(totalMensajes)
    resultados.append(totalAgresiones)
    resultados.append(porcentaje)
    resultados.append(usuarioVictima)
    resultados.append(usuarioAgresor)
    
    return resultados

# funcion que analiza un texto y regresa 1 si es agresiva o 0 si no
def analizaTexto(texto):
    from sklearn.base import ClassifierMixin
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import PassiveAggressiveClassifier
    import pandas as pd
    from sklearn.model_selection import train_test_split

    #bolsa de palabras en forma de vector de tamaño de 1000 y quitando las palabras vacias tanto en ingles como español 
    tfvect = TfidfVectorizer(max_features=1000, stop_words=('english', 'spanish'))

    dataframe = pd.read_csv('train_aggressiveness.csv')
    x = dataframe['Text']
    y = dataframe['Category']

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)

    tfid_x_train = tfvect.fit_transform(x_train)
    tfid_x_test = tfvect.transform(x_test)
    print(f"Vocabulario total: {len(tfvect.vocabulary_)} palabras")

    #creamos un objeto de la clase PassiveAggressiveClassifier
    classifier = PassiveAggressiveClassifier(max_iter=110)
    tfid_x_train = tfvect.fit_transform(x_train)
    tfid_x_test = tfvect.transform(x_test)

    #La funcion fit del objeto TfidfVectorizer aprende el vocabulario y idf del conjunto de entrenamiento dado
    classifier.fit(tfid_x_train,y_train)

    input_data = [texto]
        
    #vectorizamos el texto
    vectorized_input_data = tfvect.transform(input_data)
        
    #Hacemos le prediccion mediante el texto ya vectorizado
    prediction = classifier.predict(vectorized_input_data)
    
    #imprimos la matriz vectorizada
    print(vectorized_input_data)
        
    _, col_index = vectorized_input_data.nonzero()
        
    #Total de palabras
    print(f"Palabras totales que se tomaron de referencia: {len(col_index)}")
                
    #Imprime las palabras
    for i in col_index:
        print(sorted(list(tfvect.vocabulary_))[i])

    return prediction

def conviertePDF():
    import jinja2
    from jinja2.environment import Template
    import pdfkit
    from pdfkit.api import configuration
    

    #generamos nuestro PDF por medio de la libreria pdfkit(ruta-del-archivo-ejecutable-de-la-ruta-externa)
    config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')

    #Ruta donde se va a escribir el documento PDF
    ruta_salida = '/Users/alanmartinezruiz/Desktop/FINAL LABORATORIO TEMATICO 4/uploads/envia.pdf'
    

    
    #rescribimos nuestro documento pdf (cadenaHtml, rutaSalida, estilos, diccionarioConfiguracionDePaginas, rutaDelArchivoEjecutableInstaldo)
    #pdfkit.from_string(html, ruta_salida, css=rutacss, options=options, configuration=config)
    #pdfkit.from_string(html, ruta_salida,css=rutacss, configuration=config)
    pdfkit.from_url('http://127.0.0.1:5000/chat/message_1.json', ruta_salida, configuration=config)

def enviaMail(correo):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders
        
    # Iniciamos los parámetros del script
    remitente = 'laboratoriotem41@gmail.com'
    destinatarios = [correo]
    asunto = 'Evidencias de analisis'
    cuerpo = 'Gracias por usar nuestra aplicación'
    ruta_adjunto = '/Users/alanmartinezruiz/Desktop/FINAL LABORATORIO TEMATICO 4/uploads/envia.pdf'
    nombre_adjunto = 'Evidencias.pdf'

    # Creamos el objeto mensaje
    mensaje = MIMEMultipart()
    
    # Establecemos los atributos del mensaje
    mensaje['From'] = remitente
    mensaje['To'] = ", ".join(destinatarios)
    mensaje['Subject'] = asunto
    
    # Agregamos el cuerpo del mensaje como objeto MIME de tipo texto
    mensaje.attach(MIMEText(cuerpo, 'plain'))
    
    # Abrimos el archivo que vamos a adjuntar
    archivo_adjunto = open(ruta_adjunto, 'rb')
    
    # Creamos un objeto MIME base
    adjunto_MIME = MIMEBase('application', 'octet-stream')
    # Y le cargamos el archivo adjunto
    adjunto_MIME.set_payload((archivo_adjunto).read())
    # Codificamos el objeto en BASE64
    encoders.encode_base64(adjunto_MIME)
    # Agregamos una cabecera al objeto
    adjunto_MIME.add_header('Content-Disposition', "attachment; filename= %s" % nombre_adjunto)
    # Y finalmente lo agregamos al mensaje
    mensaje.attach(adjunto_MIME)
    
    # Creamos la conexión con el servidor
    sesion_smtp = smtplib.SMTP('smtp.gmail.com', 587)
    
    # Ciframos la conexión
    sesion_smtp.starttls()

    # Iniciamos sesión en el servidor
    sesion_smtp.login('laboratoriotem4@gmail.com','123456787654321')

    # Convertimos el objeto mensaje a texto
    texto = mensaje.as_string()

    # Enviamos el mensaje
    sesion_smtp.sendmail(remitente, destinatarios, texto)

    # Cerramos la conexión
    sesion_smtp.quit()