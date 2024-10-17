import smtplib
import secrets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from psycopg2.extras import RealDictCursor
from conexion import get_db_connection, release_db_connection  # Importa las funciones de conexión

# Función para generar un token aleatorio
def generar_token():
    return secrets.token_urlsafe(64)

# Función para enviar el correo de recuperación de contraseña
def enviar_correo_recuperacion(email_destino, token):
    remitente = "aguyjepy1@gmail.com"
    asunto = "Recupera tu contraseña - AguyjePY"
    enlace_recuperacion = f"http://localhost:5000/reset-password/{token}"

    # Crear el mensaje en HTML con estilos
    cuerpo = f"""
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
            p {{
                color: #555;
            }}
            a {{
                color: #0066cc; /* Color del enlace */
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Recupera tu contraseña</h2>
            <p>Hola,</p>
            <p>Puedes restablecer tu contraseña haciendo clic en el siguiente enlace:</p>
            <p><a href="{enlace_recuperacion}">Restablecer Contraseña</a></p>
            <p>Si no solicitaste este cambio, ignora este correo.</p>
            <p>Atentamente,<br>El equipo de AguyjePY</p>
        </div>
    </body>
    </html>
    """

    # Configuración del mensaje
    mensaje = MIMEMultipart()
    mensaje["From"] = remitente
    mensaje["To"] = email_destino
    mensaje["Subject"] = asunto
    mensaje.attach(MIMEText(cuerpo, "html"))

    # Enviar el correo
    try:
        servidor = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        servidor.login(remitente, "gqgpbgbclxbtpxnw")
        servidor.sendmail(remitente, email_destino, mensaje.as_string())
        servidor.quit()
        print(f"Correo de recuperación enviado a {email_destino}")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")


# Función para manejar la solicitud de recuperación de contraseña
def solicitar_recuperacion_contrasena(email):
    conn = get_db_connection()  # Conexión a la base de datos
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Verificar si el correo existe
            cursor.execute("SELECT usuario_id FROM usuario WHERE email = %s", (email,))
            usuario = cursor.fetchone()

            if not usuario:
                return {"error": "El correo no está registrado."}

            # Generar un token y actualizarlo en la base de datos
            token = generar_token()
            cursor.execute(
                "UPDATE usuario SET token_activacion = %s WHERE email = %s",
                (token, email)
            )
            conn.commit()

            # Enviar el correo de recuperación
            enviar_correo_recuperacion(email, token)
            return {"message": "Se ha enviado un correo para restablecer tu contraseña."}

    except Exception as e:
        print(f"Error: {e}")
        return {"error": "Hubo un error al procesar la solicitud."}
    finally:
        release_db_connection(conn)  # Liberar la conexión

