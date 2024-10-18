from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from usuario import registrar_usuario, obtener_usuarios, verificar_usuario, obtener_usuario_por_id, actualizar_usuario
from pedido_ayuda import obtener_pedidos_finalizados, finalizar_pedido_ayuda, insertar_pedido_ayuda, actualizar_pedido_ayuda, obtener_pedido_ayuda, obtener_pedido_ayuda_por_id, obtener_pedido_ayuda_usuario
from cateogoria import obtener_categorias
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
@app.route('/register', methods=['POST'])
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

# Ruta para listar todos los pedidos de ayuda
@app.route('/pedido_ayuda', methods=['GET'])
def listar_pedidos():
    pedidos = obtener_pedido_ayuda()
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

if __name__ == '__main__':
    app.run(debug=True)
