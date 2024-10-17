from conexion import get_db_connection, release_db_connection
import traceback
import psycopg2.extras  # Importa el módulo para usar DictCursor
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import traceback
import uuid  # Para generar el token único


def verificar_usuario(email, password):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            query = """
                SELECT * FROM usuario WHERE email = %s AND password = %s AND cuenta_activa = TRUE
            """
            print(f"Consulta SQL: {query}")  # Imprime la consulta SQL
            print(f"Datos enviados: email={email}, password={password}")  # Imprime los datos enviados
            
            cursor.execute(query, (email, password))
            
            usuario = cursor.fetchone()  # Esto ahora será un diccionario
            
            print(f"Resultado de la consulta: {usuario}")  # Imprime el resultado de la consulta
            
            return usuario
    except Exception as e:
        print(f"Error al verificar usuario: {e}")
        print(traceback.format_exc())  # Imprime el traceback completo del error
        return None
    finally:
        release_db_connection(conn)



# Función para enviar correo de activación
def enviar_correo_activacion(email_destinatario, token_activacion):
    remitente = "aguyjepy1@gmail.com"
    clave_app = "gqgpbgbclxbtpxnw"  # Tu código de aplicación de Gmail
    asunto = "Activa tu cuenta en AguyjePY"
    
    # Generar el enlace de activación
    enlace_activacion = f"http://localhost:5000/activar_cuenta/{token_activacion}"

    # Crear el mensaje en HTML con estilos
    mensaje_html = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4ccf4; /* Color de fondo */
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    background-color: white;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                }}
                h2 {{
                    color: #333;
                }}
                a {{
                    color: #0066cc; /* Color del enlace */
                    text-decoration: none;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Bienvenido a AguyjePY</h2>
                <p>Gracias por registrarte. Por favor, haz clic en el siguiente enlace para activar tu cuenta:</p>
                <a href="{enlace_activacion}">Activar mi cuenta</a>
                <p>Si no solicitaste esta cuenta, puedes ignorar este correo.</p>
            </div>
        </body>
    </html>
    """

    # Crear el correo electrónico
    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = email_destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(mensaje_html, 'html'))

    try:
        # Conectar al servidor SMTP de Gmail
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()
        servidor.login(remitente, clave_app)
        
        # Enviar el correo
        servidor.sendmail(remitente, email_destinatario, msg.as_string())
        servidor.quit()
        print(f"Correo de activación enviado a {email_destinatario}")
        return True
    except Exception as e:
        print(f"Error al enviar el correo de activación: {e}")
        print(traceback.format_exc())
        return False


# Modificar la función registrar_usuario
def registrar_usuario(data):
    conn = get_db_connection()
    try:
        print("Datos recibidos para registrar usuario:", data)
        
        token_activacion = str(uuid.uuid4())  # Generar un token único para la activación
        
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO usuario (nombre, apellido, doc_identidad, celular, direccion, email, ciudad_id, barrio, password, token_activacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data.get('nombres') or None, 
                data.get('apellidos') or None, 
                int(data.get('cedula') or 0),  # Asume 0 si no hay cédula
                int(data.get('celular') or 0),  # Asume 0 si no hay celular
                data.get('direccion') or None, 
                data.get('correo') or None, 
                int(data.get('ciudad') or 3),   # Asume 3 si no hay ciudad
                data.get('barrio') or None, 
                data.get('password') or None, 
                token_activacion  # Token de activación
            ))
            conn.commit()

            # Enviar correo de activación
            if enviar_correo_activacion(data.get('correo'), token_activacion):
                return True
            else:
                return False
    except Exception as e:
        print(f"Error al registrar usuario: {e}")
        print(traceback.format_exc())
        return False
    finally:
        release_db_connection(conn)


def obtener_usuario_por_id(usuario_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
             SELECT 
    u.usuario_id,
    u.nombre,
    u.apellido,
    u.doc_identidad,
    u.celular,
    u.direccion,
    u.email,
    u.ciudad_id,
    c.descripcion AS nombre_ciudad,
    u.barrio,
    u.password
FROM 
    usuario u
JOIN 
    ciudad c
ON 
    u.ciudad_id = c.ciudad_id                                
                           WHERE u.usuario_id = %s
            """, (usuario_id,))
            usuario = cursor.fetchone()

            if usuario:
                return {
                    'usuario_id': usuario[0],
                    'nombre': usuario[1],
                    'apellido': usuario[2],
                    'doc_identidad': usuario[3],
                    'celular': usuario[4],
                    'direccion': usuario[5],
                    'email': usuario[6],
                    'ciudad_id': usuario[7],
                    'nombre_ciudad': usuario[8],
                    'barrio': usuario[9],
                    'password': usuario[10]
                }
            else:
                return None
    except Exception as e:
        print(f"Error al obtener usuario por ID: {e}")
        print(traceback.format_exc())  # Imprime el traceback completo del error
        return None
    finally:
        release_db_connection(conn)

def obtener_usuarios():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM usuario")
            usuarios = cursor.fetchall()

            usuarios_list = []
            for usuario in usuarios:
                usuarios_list.append({
                    'usuario_id': usuario[0],
                    'nombre': usuario[1],
                    'apellido': usuario[2],
                    'doc_identidad': usuario[3],
                    'celular': usuario[4],
                    'direccion': usuario[5],
                    'email': usuario[6],
                    'ciudad_id': usuario[7],
                    'barrio': usuario[8],
                    'contraseña': usuario[9],
                    'grupo_usuario_id': usuario[10]
                })

            return usuarios_list
    except Exception as e:
        print(f"Error al obtener usuarios: {e}")
        print(traceback.format_exc())  # Imprime el traceback completo del error
        return []
    finally:
        release_db_connection(conn)


def actualizar_usuario(usuario_id, data):
    conn = get_db_connection()
    try:
        # Imprimir los datos recibidos para depuración
        print(f"Datos recibidos para actualizar usuario con ID {usuario_id}:", data)
        
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE usuario
                SET nombre = %s,
                    apellido = %s,
                    doc_identidad = %s,
                    celular = %s,
                    direccion = %s,
                    ciudad_id = %s,
                    barrio = %s,
                    email = %s
                WHERE usuario_id = %s
            """, (
                data.get('nombres') or None, 
                data.get('apellidos') or None, 
                int(data.get('cedula') or 0),  # Asume 0 si no hay cédula
                int(data.get('celular') or 0),  # Asume 0 si no hay celular
                data.get('direccion') or None, 
                data.get('ciudad') or None, 
                data.get('barrio') or None, 
                data.get('correo') or None, 
                usuario_id
            ))
            conn.commit()
            return True
    except Exception as e:
        print(f"Error al actualizar usuario con ID {usuario_id}: {e}")
        print(traceback.format_exc())
        return False
    finally:
        release_db_connection(conn)
