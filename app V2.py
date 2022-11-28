from PIL import Image, ImageDraw, ImageFont
import img2pdf 
from flask import Flask
from flask import render_template, request, redirect, url_for, flash
from flaskext.mysql import MySQL
import smtplib
from decouple import config
from datetime import datetime #cambiar el nombre de la foto
import os
import pandas as pd 
import numpy as np
from sqlalchemy import create_engine
from sklearn.datasets import load_iris

app=Flask(__name__)

app.secret_key="Develoteca" #Para enviar mensajes de alerta

mysql=MySQL()
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='pruebamigracion'
mysql.init_app(app) #Crear la conexion con los datos anteriores asignados

#mostrar formulario de creación 
@app.route('/')
def index():
    return render_template('inicio.html')

@app.route('/buscarCertificado', methods=['POST'])
def buscar():
    _identificacion=request.form['txtIde']
    if _identificacion=='':
        flash('Recuerda llenar los datos del nombre del evaluador, correo y su correspondiente evaluación')
    else:
        sql="SELECT * FROM persona WHERE Identificacion=%s"
        datos=(_identificacion)
        conn=mysql.connect() #Conectarse a la base de datos
        cursor=conn.cursor() #Almacenar la instruccion SQL
        cursor.execute(sql, datos)
        fila=cursor.fetchall()
        datosRecibidos=cursor.rowcount
        conn.commit() 
        if datosRecibidos ==1:
            # adjust the position according to your sample
            text_y_position_Nombre = 300
            # opens the image
            image = Image.open("Certificate.png")
            # path to font
            fontNombre = ImageFont.truetype("arial.ttf", 60)
            fontProyecto = ImageFont.truetype("arial.ttf", 20)
            # gets the image width
            image_width = image.width
            #text width
            text_widthNombre, _=fontNombre.getsize(fila[0][1])
        
            draw = ImageDraw.Draw(image)
            #escribe el NOMBRE en la imagen
            draw.text(((image_width - text_widthNombre) / 2,text_y_position_Nombre), fila[0][1], font=fontNombre, fill="red")
            #escribe el PROYECTO en la imagen
            draw.text((360,432), fila[0][3], font=fontProyecto, fill="red")
            #escribe la MODALIDAD en la imagen
            draw.text((730,462), fila[0][4], font=fontProyecto, fill="red")
            #guarda la imagen- inicio
            image.save(_identificacion+".png")
            image.save("CertificadosGenerados/"+_identificacion+".png")
            #Convertir imagen en pdf
            img_path = "CertificadosGenerados/"+_identificacion+".png" #ubicacion de la imagen
            pdf_path = "CertificadosGenerados/"+_identificacion+".pdf" #ubicacion del pdf a crear
            image = Image.open(img_path)
            pdf_bytes = img2pdf.convert(image.filename) 
            file = open(pdf_path, "wb")
            file.write(pdf_bytes) 
            image.close() 
            file.close()
            flash('Certificado generado', category="info")
            #Convertir imagen en pdf fin 
            #Abrir pdf
            path = 'CertificadosGenerados\\'+_identificacion+'.pdf'
            os.startfile(path)
           
        if datosRecibidos ==0:
            flash('Usuario no registrado en el sistema, comuniquese con la División de Investigación Formativa', category="info")

    return redirect('/')


@app.route('/proyecto')
def proyecto():
    return render_template('proyecto.html')


@app.route('/buscarProyecto', methods=['POST'])
def buscarProyecto():
    _codigo=request.form['txtCodigo']
    conn=mysql.connect() #Conectarse a la base de datos
    cursor=conn.cursor() #Almacenar la instruccion SQL
    #Buscar el proyecto
    cursor.execute("SELECT pr.id, pr.codigo, pr.Nombre_Proyecto, pr.Modalidad, aut.Nombre AS Autor, pr.Evaluador, pr.Evaluacion FROM proyecto pr, persona aut WHERE pr.codigo=%s AND pr.Autor = aut.Id", _codigo)
    infoProyecto=cursor.fetchall() #devolver toda la informacion la consulta 
    datosRecibidos=cursor.rowcount
    conn.commit()
    if datosRecibidos ==0:
        flash('No existe el proyecto', category="info")
        return render_template('proyecto.html')

    else:
        return render_template('infoProyecto.html', infoProyecto=infoProyecto)
    
@app.route('/buscarProyecto2/<int:id>')
def buscarProyecto2(id):
 
    conn=mysql.connect() #Conectarse a la base de datos
    cursor=conn.cursor() #Almacenar la instruccion SQL
    #Buscar el proyecto
    cursor.execute("SELECT pr.id, pr.codigo, pr.Nombre_Proyecto, pr.Modalidad, aut.Nombre AS Autor, pr.Evaluador, pr.Evaluacion FROM proyecto pr, persona aut WHERE pr.codigo=%s AND pr.Autor = aut.Id", id)
    infoProyecto=cursor.fetchall() #devolver toda la informacion la consulta 
    conn.commit() 
    return render_template('infoProyecto.html', infoProyecto=infoProyecto)
    
@app.route('/ListadoProyecto')
def ListadoProyecto():
    sql="SELECT * FROM proyecto;"
    conn=mysql.connect() #Conectarse a la base de datos
    cursor=conn.cursor() #Almacenar la instruccion SQL
    cursor.execute(sql) #Ejecutar la instruccion almacenada
    ListaP=cursor.fetchall() #devolver toda la informacion la consulta 
    conn.commit() #Cerrar la conexion que se realizó antes
    return render_template('ListadoProyectos.html', ListaP=ListaP)

@app.route('/update', methods=['POST'])
def update():
    _codigo=request.form['txtCodigo']
    _evaluacion=request.form['txtEvaluacion']
    _evaluador=request.form['txtEvaluador']
    _correo=request.form['txtCorreoEvaluador']

    if _evaluacion=='' or _evaluador=='' or _correo=='':
        flash('Recuerda llenar los datos del nombre del evaluador, correo y su correspondiente evaluación', category="info")
        conn=mysql.connect() #Conectarse a la base de datos
        cursor=conn.cursor() #Almacenar la instruccion SQL
        #Buscar el proyecto
        cursor.execute("SELECT pr.id, pr.codigo, pr.Nombre_Proyecto, pr.Modalidad, aut.Nombre AS Autor, pr.Evaluador, pr.Evaluacion FROM proyecto pr, persona aut WHERE pr.codigo=%s AND pr.Autor = aut.Id", _codigo)
        infoProyecto=cursor.fetchall() #devolver toda la informacion la consulta 
        conn.commit() 
        return render_template('infoProyecto.html', infoProyecto=infoProyecto)
        
    else:
        #Actualiza el evaluador y la evaluacion del proyecto
        conn=mysql.connect() #Conectarse a la base de datos
        cursor=conn.cursor() #Almacenar la instruccion SQL    
        sql="UPDATE proyecto SET Evaluacion= %s , Evaluador= %s WHERE codigo= %s;"
        datos=(_evaluacion, _evaluador, _codigo)
        cursor.execute(sql, datos)
        conn.commit() #Cerrar la conexion que se realizó antes
        # Crea o actualiza el evaluador en la tabla persona
        conn=mysql.connect() #Conectarse a la base de datos
        cursor=conn.cursor() #Almacenar la instruccion SQL
        cursor.execute("SELECT * FROM persona WHERE correo=%s", _correo)
        ExisteEvaluador=cursor.rowcount
        if ExisteEvaluador==0:
            sql="INSERT INTO persona (id, Nombre, Rol, correo) VALUES (NULL, %s, %s, %s);"
            datos=(_evaluador, 2, _correo)
            cursor=conn.cursor()
            cursor.execute(sql, datos)
            conn.commit() #Cerrar la conexion que se realizó antes
        else: 
            conn=mysql.connect() #Conectarse a la base de datos
            cursor=conn.cursor() #Almacenar la instruccion SQL    
            sql="UPDATE persona SET Nombre= %s WHERE correo= %s;"
            datos=(_evaluador, _correo)
            cursor.execute(sql, datos)
            conn.commit() #Cerrar la conexion que se realizó antes
        #Consulta los datos del proyecto para enviar el correo
        cursor.execute("SELECT * FROM proyecto WHERE codigo=%s", _codigo)
        fila=cursor.fetchall()
        nombre_Proyecto=fila[0][2]
        desc_Evalua=fila[0][6]
        datosRecibidos2=cursor.rowcount
        
        if datosRecibidos2 >0:
            #Guardar correo al evaluador del proyecto
            ListaCorreos=[_correo]
            #Consultar correo de los autores
            cursor.execute("SELECT * FROM persona WHERE Id IN (SELECT Autor FROM proyecto WHERE codigo =%s)", _codigo)
            fila=cursor.fetchall()
            datosRecibidos3=cursor.rowcount
            if datosRecibidos3 >0:
                for n in fila:
                    #Guardar los correos de los autores del proyecto
                    ListaCorreos.append(n[3]) 
                    
                #Enviar correo a evaluador y autores   
                for n in ListaCorreos:
                    destinatario=n
                    message='Cordial saludo, esto es una prueba2'
                    subject="Evaluacion de proyecto"
                    message='Cordial saludo,\n\n Se ha realizado la evaluacion del proyecto: {} \n\n Por lo tanto, se considera que:  "{}"'.format(nombre_Proyecto, desc_Evalua)
                    message='Subject: {}\n\n{}'.format(subject, message)
                    server=smtplib.SMTP('smtp.gmail.com',587)
                    server.starttls()
                    server.login('diif@uniboyaca.edu.co', config('MAIL_PASSWORD'))
                    server.sendmail('diif@uniboyaca.edu.co', destinatario, message)
                    server.quit()
                    conn.commit() #Cerrar la conexion que se realizó antes
                    
            else: 
                flash('El proyecto no tiene autores relacionados', category="info")

        else:
                flash('No se encontró el proyecto', category="info")

        return render_template('proyecto.html')

@app.route('/CargueMasivo')
def CargueMasivo():
    return render_template('cargueMasivo.html')

@app.route('/ImportarDatos/', methods=['POST'])
def ImportarDatos():
    archivo=request.files['txtArchivo']
    nombreArc=archivo.filename
    nombreArc, extArc= os.path.splitext(nombreArc)
    if extArc=='.csv':
        datos = pd.read_csv(archivo , sep=';' ,header=0, names= ['Nombre','Rol', 'correo', 'proyecto', 'Identificacion'])  
        df = pd.DataFrame(datos) 
        conn=mysql.connect()

        for row in df.itertuples():
            sql="INSERT INTO persona (Id, Nombre, Rol, correo, proyecto, Identificacion) VALUES (NULL, %s,%s,%s,%s,%s);"
    
            datos=(
                row.Nombre,
                row.Rol,
                row.correo,
                row.proyecto,
                row.Identificacion)

            cursor=conn.cursor()
            cursor.execute(sql, datos)
            
        conn.commit() #Cerrar la conexion que se realizó antes 
        flash('Se ha cargado la información exitosamente en la base de datos', category="success")
   
            
    else: 
        flash('El archivo debe tener extensión .csv', category="error")
    
    return render_template('cargueMasivo.html')
    

if __name__=='__main__':
    app.run(debug=True)
    