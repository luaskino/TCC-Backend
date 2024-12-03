from conexion import get_db_connection, release_db_connection
import traceback
import psycopg2.extras
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_correo(destinatario, nombre, descripcion_pedido):
    remitente = "aguyjepy1@gmail.com"
    servidor = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    servidor.login(remitente, "gqgpbgbclxbtpxnw")

    asunto = "Nuevo Pedido de Ayuda Registrado"
    cuerpo = f"""
    Hola {nombre},

    Se ha registrado un nuevo pedido de ayuda con la siguiente descripción:

    "{descripcion_pedido}"

    Gracias por tu atención.

    Saludos,
    El equipo de Ayuda
    """

    mensaje = MIMEMultipart()
    mensaje['From'] = remitente
    mensaje['To'] = destinatario
    mensaje['Subject'] = asunto
    mensaje.attach(MIMEText(cuerpo, 'plain'))

    try:
        servidor.sendmail(remitente, destinatario, mensaje.as_string())
        print(f"Correo enviado a {destinatario}")
    except Exception as e:
        print(f"Error al enviar correo a {destinatario}: {e}")
    finally:
        servidor.quit()

def insertar_pedido_ayuda(data):
    conn = get_db_connection()
    try:
        print("Datos recibidos para registrar pedido de ayuda:", data)
        with conn.cursor() as cursor:
            # Insertar el pedido principal
            cursor.execute("""
                INSERT INTO pedido_ayuda (usuario_id, categoria_id, descripcion, fecha, estado, ubicacion)
                VALUES (%s, %s, %s, CURRENT_DATE, %s, %s) RETURNING pedido_id
            """, (
                int(data.get('usuario_id')),
                int(data.get('categoria_id')),
                data.get('descripcion'),
                data.get('estado') or None,
                data.get('ubicacion')
            ))
            pedido_id = cursor.fetchone()[0]

            # Insertar los detalles opcionales si existen
            if 'detalles' in data and isinstance(data['detalles'], list):
                for detalle in data['detalles']:
                    cursor.execute("""
                        INSERT INTO pedido_ayuda_detalle (pedido_id, item_nombre, cantidad)
                        VALUES (%s, %s, %s)
                    """, (
                        pedido_id,
                        detalle['item_nombre'],
                        int(detalle['cantidad'])
                    ))

            conn.commit()

            # Obtener usuarios con cuenta activa para enviar correos
            cursor.execute("""
                SELECT nombre, email FROM usuario WHERE cuenta_activa = true
            """)
            usuarios_activos = cursor.fetchall()

            descripcion_pedido = data.get('descripcion')
            for usuario in usuarios_activos:
                nombre, email = usuario
                enviar_correo(email, nombre, descripcion_pedido)

            return True
    except Exception as e:
        print(f"Error al registrar pedido de ayuda: {e}")
        print(traceback.format_exc())
        return False
    finally:
        release_db_connection(conn)


def finalizar_pedido_ayuda(pedido_id):
    conn = get_db_connection()  # Obtener la conexión a la base de datos
    try:
        with conn.cursor() as cursor:
            # Actualizar el estado del pedido a 'finalizado'
            cursor.execute("""
                UPDATE pedido_ayuda
                SET estado = 'finalizado'
                WHERE pedido_id = %s
            """, (pedido_id,))
            
            # Verificar si se actualizó alguna fila
            if cursor.rowcount == 0:
                return {"success": False, "message": "Pedido no encontrado"}, 404

            conn.commit()  # Confirmar la transacción
            return {"success": True, "message": "Pedido finalizado correctamente"}, 200
    except Exception as e:
        print(f"Error al finalizar el pedido de ayuda: {e}")
        print(traceback.format_exc())
        return {"success": False, "message": "Error interno del servidor"}, 500
    finally:
        release_db_connection(conn)  # Liberar la conexión a la base de datos


def actualizar_pedido_ayuda(pedido_id, data):
    conn = get_db_connection()
    try:
        print(f"Datos recibidos para actualizar pedido de ayuda con ID {pedido_id}:", data)
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE pedido_ayuda
                SET usuario_id = %s,
                    categoria_id = %s,
                    descripcion = %s,
                    estado = %s,
                    ubicacion = %s
                WHERE pedido_id = %s
            """, (
                int(data.get('usuario_id')),
                int(data.get('categoria_id')),
                data.get('descripcion'),
                data.get('estado') or None,
                data.get('ubicacion'),
                pedido_id
            ))
            conn.commit()
            return True
    except Exception as e:
        print(f"Error al actualizar pedido de ayuda con ID {pedido_id}: {e}")
        print(traceback.format_exc())
        return False
    finally:
        release_db_connection(conn)

def obtener_pedido_ayuda():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute('''SELECT
    pa.pedido_id,
    pa.categoria_id,
    pa.descripcion,
    pa.fecha,
    pa.estado,
    pa.ubicacion,
    u.nombre || ' ' || u.apellido AS nombre_completo,
    u.celular,
    u.email,
    u.direccion,
    c.descripcion AS ciudad
FROM
    pedido_ayuda pa
JOIN
    usuario u ON pa.usuario_id = u.usuario_id
JOIN
    ciudad c ON u.ciudad_id = c.ciudad_id where pa.estado='pendiente';
''')
            pedidos = cursor.fetchall()
            return [dict(pedido) for pedido in pedidos]
    except Exception as e:
        print(f"Error al obtener pedidos de ayuda: {e}")
        print(traceback.format_exc())
        return []
    finally:
        release_db_connection(conn)


def obtener_pedido_ayuda_todos():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute('''SELECT
    pa.pedido_id,
    pa.categoria_id,
    pa.descripcion,
    pa.fecha,
    pa.estado,
    pa.ubicacion,
    u.nombre || ' ' || u.apellido AS nombre_completo,
    u.celular,
    u.email,
    u.direccion,
    c.descripcion AS ciudad
FROM
    pedido_ayuda pa
JOIN
    usuario u ON pa.usuario_id = u.usuario_id
JOIN
    ciudad c ON u.ciudad_id = c.ciudad_id;
''')
            pedidos = cursor.fetchall()
            return [dict(pedido) for pedido in pedidos]
    except Exception as e:
        print(f"Error al obtener pedidos de ayuda: {e}")
        print(traceback.format_exc())
        return []
    finally:
        release_db_connection(conn)



def obtener_pedidos_finalizados():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute('''SELECT
    pa.pedido_id,
    pa.categoria_id,
    pa.descripcion,
    pa.fecha,
    pa.estado,
    pa.ubicacion,
    u.nombre || ' ' || u.apellido AS nombre_completo,
    u.celular,
    u.email,
    u.direccion,
    c.descripcion AS ciudad
FROM
    pedido_ayuda pa
JOIN
    usuario u ON pa.usuario_id = u.usuario_id
JOIN
    ciudad c ON u.ciudad_id = c.ciudad_id where pa.estado='finalizado';
''')
            pedidos = cursor.fetchall()
            return [dict(pedido) for pedido in pedidos]
    except Exception as e:
        print(f"Error al obtener pedidos de ayuda: {e}")
        print(traceback.format_exc())
        return []
    finally:
        release_db_connection(conn)


def obtener_pedido_ayuda_usuario(usuario_id):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute('''SELECT
                pa.pedido_id,
                pa.categoria_id,
                pa.descripcion AS descripcion_pedido,
                pa.fecha,
                pa.estado,
                pa.ubicacion,
                u.nombre || ' ' || u.apellido AS nombre_completo,
                u.celular,
                u.email,
                u.direccion,
                c.descripcion AS ciudad,
                cat.descripcion AS categoria_descripcion  -- Agregar descripción de la categoría
            FROM
                pedido_ayuda pa
            JOIN
                usuario u ON pa.usuario_id = u.usuario_id
            JOIN
                ciudad c ON u.ciudad_id = c.ciudad_id
            JOIN
                categoria_donacion cat ON pa.categoria_id = cat.categoria_id  -- Unir con categoría
            WHERE
                pa.usuario_id = %s;
            ''', (usuario_id,))
            pedidos = cursor.fetchall()
            return [dict(pedido) for pedido in pedidos]  # Retornar los pedidos sin jsonify
    except Exception as e:
        print(f"Error al obtener pedidos de ayuda: {e}")
        print(traceback.format_exc())
        return []  # Retornar lista vacía en caso de error
    finally:
        release_db_connection(conn)


def obtener_pedido_ayuda_por_id(pedido_id):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM pedido_ayuda WHERE pedido_id = %s
            """, (pedido_id,))
            pedido = cursor.fetchone()
            return dict(pedido) if pedido else None
    except Exception as e:
        print(f"Error al obtener pedido de ayuda con ID {pedido_id}: {e}")
        print(traceback.format_exc())
        return None
    finally:
        release_db_connection(conn)

def obtener_totales_pedidos():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute('''
                SELECT estado, COUNT(*) as total
                FROM pedido_ayuda
                WHERE estado IN ('finalizado', 'pendiente')
                GROUP BY estado;
            ''')
            resultados = cursor.fetchall()
            
            # Transformar los resultados en un diccionario para una respuesta fácil de manejar
            totales = {row['estado']: row['total'] for row in resultados}
            return totales
    except Exception as e:
        print(f"Error al obtener totales de pedidos: {e}")
        print(traceback.format_exc())
        return {}
    finally:
        release_db_connection(conn)