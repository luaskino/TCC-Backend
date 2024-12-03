from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from usuario import registrar_usuario, obtener_usuarios, verificar_usuario, obtener_usuario_por_id, actualizar_usuario
from pedido_ayuda import obtener_pedidos_finalizados, finalizar_pedido_ayuda, insertar_pedido_ayuda, actualizar_pedido_ayuda, obtener_pedido_ayuda, obtener_pedido_ayuda_todos, obtener_pedido_ayuda_por_id, obtener_pedido_ayuda_usuario, obtener_totales_pedidos
from cateogoria import obtener_categorias
from encuesta import insertar_encuesta, obtener_encuesta_id
from ciudad import obtener_ciudad
from conexion import get_db_connection, release_db_connection
from solicitar_recuperacion import solicitar_recuperacion_contrasena

app = Flask(__name__)
CORS(app)

# Ruta para el login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = verificar_usuario(email, password)

    if user:
        return jsonify({
            'message': 'Inicio de sesión exitoso',
            'usuario_id': user['usuario_id'],  # Retornar usuario_id
            'nombre': user['nombre']  # Retornar nombre
        })
    else:
        return jsonify({'message': 'Credenciales inválidas'}), 401

@app.route('/solicitar-recuperacion', methods=['POST'])
def solicitar_recuperacion():
    data = request.get_json()
    email = data.get('email')
    
    result = solicitar_recuperacion_contrasena(email)  # Llama a la función
    if "error" in result:
        return jsonify(result), 400  # Retorna error si existe
    return jsonify(result), 200  # Retorna mensaje de éxito

@app.route('/finalizar_pedido_ayuda/<int:pedido_id>', methods=['PUT'])
def finalizar_pedido(pedido_id):
    resultado, status_code = finalizar_pedido_ayuda(pedido_id)
    return jsonify(resultado), status_code

@app.route('/reset-password/<token>', methods=['GET'])
def reset_password_form(token):
    return render_template('reset_password.html', token=token)

@app.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    data = request.get_json()  # Obtiene el JSON enviado
    
    # Log para verificar qué datos se reciben
    print(f"Datos recibidos: {data}")

    nueva_contrasena = data.get('nueva_contrasena')  # Obtiene la nueva contraseña

    if not nueva_contrasena:
        return jsonify({"error": "La nueva contraseña es requerida."}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Verificar el token
            cursor.execute("SELECT usuario_id FROM usuario WHERE token_activacion = %s", (token,))
            usuario = cursor.fetchone()

            if not usuario:
                return jsonify({"error": "Token inválido."}), 400

            # Actualizar la contraseña
            cursor.execute(
                "UPDATE usuario SET password = %s, token_activacion = NULL WHERE usuario_id = %s",
                (nueva_contrasena, usuario[0])
            )
            conn.commit()

            return jsonify({"message": "Contraseña restablecida exitosamente."}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Hubo un error al restablecer la contraseña."}), 500
    finally:
        release_db_connection(conn)


# Ruta para registrar un usuario
@app.route('/registro', methods=['POST'])
def register():
    data = request.get_json()
    if registrar_usuario(data):
        return jsonify({'message': 'Usuario registrado exitosamente'}), 201
    else:
        return jsonify({'message': 'Error al registrar usuario'}), 500

# Ruta para obtener un usuario por ID
@app.route('/usuarios/<int:usuario_id>', methods=['GET'])
def get_usuario(usuario_id):
    usuario = obtener_usuario_por_id(usuario_id)
    if usuario:
        return jsonify(usuario)
    else:
        return jsonify({'message': 'Usuario no encontrado'}), 404

# Ruta para obtener todos los usuarios
@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    usuarios = obtener_usuarios()
    return jsonify(usuarios)

# Ruta para actualizar un usuario
@app.route('/usuarios/<int:usuario_id>', methods=['PUT'])
def update_usuario(usuario_id):
    data = request.get_json()
    if actualizar_usuario(usuario_id, data):
        return jsonify({'message': 'Usuario actualizado exitosamente'})
    else:
        return jsonify({'message': 'Error al actualizar usuario'}), 500


# ------------------- Rutas para pedido_ayuda -------------------

# Ruta para insertar un nuevo pedido de ayuda
@app.route('/pedido_ayuda', methods=['POST'])
def insertar_pedido():
    data = request.get_json()
    if insertar_pedido_ayuda(data):
        return jsonify({'message': 'Pedido de ayuda registrado exitosamente'}), 201
    else:
        return jsonify({'message': 'Error al registrar pedido de ayuda'}), 500

@app.route('/encuesta', methods=['POST'])
def guardar_encuesta():
    data = request.json  # Obtener los datos en formato JSON del cuerpo de la solicitud
    if not all(key in data for key in ('pedido_id', 'usuario_id', 'ayudaste')):
        return jsonify({'error': 'Faltan datos necesarios'}), 400

    # Llamar a la función para insertar la encuesta en la base de datos
    if insertar_encuesta(data):
        return jsonify({'message': 'Encuesta guardada exitosamente'}), 201
    else:
        return jsonify({'error': 'Error al guardar la encuesta'}), 500

@app.route('/encuesta/<int:encuesta_id>', methods=['GET'])
def api_obtener_encuesta(encuesta_id):
    encuesta = obtener_encuesta_id(encuesta_id)
    if encuesta:
        return jsonify(encuesta), 200  # Retorna la encuesta en formato JSON
    else:
        return jsonify({'error': 'Encuesta no encontrada'}), 404  # Retorna un error si no se encuentra la encuesta


# Ruta para listar todos los pedidos de ayuda
@app.route('/pedido_ayuda', methods=['GET'])
def listar_pedidos():
    pedidos = obtener_pedido_ayuda()
    return jsonify(pedidos)

# Ruta para listar todos los pedidos de ayuda
@app.route('/pedido_ayuda_todos', methods=['GET'])
def listar_pedidos_todos():
    pedidos = obtener_pedido_ayuda_todos()
    return jsonify(pedidos)


# Ruta para listar todos los pedidos de ayuda
@app.route('/pedidos_finalizados', methods=['GET'])
def listar_pedidos_finalizados():
    pedidos = obtener_pedidos_finalizados()
    return jsonify(pedidos)

# Ruta para obtener todos los pedidos de ayuda por usuario
@app.route('/pedido_ayuda/usuario/<int:usuario_id>', methods=['GET'])
def obtener_pedidos_por_usuario(usuario_id):
    pedidos = obtener_pedido_ayuda_usuario(usuario_id)
    return jsonify(pedidos)  # Retorna la respuesta ya formateada en JSON



# Ruta para obtener un pedido de ayuda por ID
@app.route('/pedido_ayuda/<int:pedido_id>', methods=['GET'])
def obtener_pedido(pedido_id):
    pedido = obtener_pedido_ayuda_por_id(pedido_id)
    if pedido:
        return jsonify(pedido)
    else:
        return jsonify({'message': 'Pedido de ayuda no encontrado'}), 404

# Ruta para actualizar un pedido de ayuda por ID
@app.route('/pedido_ayuda/<int:pedido_id>', methods=['PUT'])
def actualizar_pedido(pedido_id):
    data = request.get_json()
    if actualizar_pedido_ayuda(pedido_id, data):
        return jsonify({'message': 'Pedido de ayuda actualizado exitosamente'})
    else:
        return jsonify({'message': 'Error al actualizar pedido de ayuda'}), 500

# Ruta para listar todos los pedidos de ayuda
@app.route('/totales_pedidos', methods=['GET'])
def totales_pedidos():
    pedidos = obtener_totales_pedidos()
    return jsonify(pedidos)

# ---------------------------------------------------------------

# Ruta para obtener todos las ciudades
@app.route('/ciudad', methods=['GET'])
def get_ciudad():
    ciudad = obtener_ciudad()
    return jsonify(ciudad)

@app.route('/activar_cuenta/<token>', methods=['GET'])
def activar_cuenta(token):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE usuario SET cuenta_activa = TRUE WHERE token_activacion = %s", (token,))
            conn.commit()

        return "Cuenta activada con éxito. Ahora puedes iniciar sesión."
    except Exception as e:
        print(f"Error al activar la cuenta: {e}")
        return "Hubo un error al activar la cuenta. Inténtalo de nuevo."
    finally:
        release_db_connection(conn)


# Ruta para obtener todos las categorias
@app.route('/categorias', methods=['GET'])
def get_categorias():
    categorias = obtener_categorias()
    return jsonify(categorias)

# Nueva ruta para obtener estadísticas de categorías
@app.route('/categorias_estadisticas', methods=['GET'])
def categorias_estadisticas():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            # Consulta para obtener el total de pedidos por categoría
            cursor.execute('''
                SELECT 
                    c.descripcion AS categoria, 
                    COUNT(pa.pedido_id) AS total_pedidos
                FROM 
                    categoria c
                LEFT JOIN 
                    pedido_ayuda pa ON c.categoria_id = pa.categoria_id
                GROUP BY 
                    c.categoria_id, c.descripcion
                ORDER BY 
                    total_pedidos DESC
            ''')
            resultados = cursor.fetchall()
            categorias_estadisticas = [
                {"categoria": row["categoria"], "total_pedidos": row["total_pedidos"]}
                for row in resultados
            ]
            return jsonify(categorias_estadisticas)
    except Exception as e:
        print(f"Error al obtener estadísticas de categorías: {e}")
        return jsonify({"error": "No se pudieron obtener las estadísticas"}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

