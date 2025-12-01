from flask import Flask, request, jsonify
from Blockchain.Blockchain import Blockchain
#import sys
import os
import requests

app = Flask(__name__)

#Obtener el puerto desde la variable de entorno FLASK_RUN_PORT
puerto = os.getenv('FLASK_RUN_PORT', 5000)  # Usa 5000 como valor predeterminado si no se encuentra la variable de entorno
blockchain = Blockchain(puerto)



#Ruta para agregar un nodo vecino
@app.route('/agregar_nodo', methods=['POST'])
def agregar_nodo():
    datos = request.get_json()
    nodo = datos.get('nodo')
    if nodo:
        blockchain.agregar_nodo(nodo)
        return jsonify({"mensaje": f"Nodo {nodo} agregado"}), 200
    return jsonify({"error": "No se proporcionó nodo"}), 400

#Ruta para obtener la cadena
@app.route('/cadena', methods=['GET'])
def obtener_cadena():
    return jsonify([bloque.to_dict() for bloque in blockchain.cadena]), 200

#Ruta para recibir bloques propagados
@app.route('/agregar_bloque', methods=['POST'])
def recibir_bloque():
    datos = request.get_json()
    
    #Verificar que todas las claves necesarias estén presentes en los datos
    if not all(key in datos for key in ['datos', 'firma', 'clave_publica', 'index', 'previous_hash', 'hash']):
        return jsonify({"error": "Faltan datos en la solicitud"}), 400
    
    try:
        nuevo_bloque = blockchain.crear_bloque(
            datos['datos'],
            datos['firma'],
            datos['clave_publica']
        )
        nuevo_bloque.index = datos['index']
        nuevo_bloque.previous_hash = datos['previous_hash']
        nuevo_bloque.hash = datos['hash']
        blockchain.cadena.append(nuevo_bloque)
        return jsonify({"mensaje": "Bloque recibido"}), 200
    except Exception as e:
        return jsonify({"error": f"Error al procesar el bloque: {str(e)}"}), 500


#Ruta para sincronizar con el nodo principal
@app.route('/sincronizar', methods=['GET'])
def sincronizar():
    try:
        response = requests.get("http://localhost:5000/cadena")
        if response.status_code == 200:
            cadena_remota = response.json()
            blockchain.cadena.clear()
            for bloque in cadena_remota:
                nuevo = blockchain.agregar_bloque(
                    bloque['datos'],
                    bloque['firma'],
                    bloque['clave_publica']
                )
                nuevo.index = bloque['index']
                nuevo.previous_hash = bloque['previous_hash']
                nuevo.hash = bloque['hash']
                blockchain.cadena[-1] = nuevo  #Reemplaza el último bloque con el bloque sincronizado
            return jsonify({"mensaje": "Sincronizado con nodo principal"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Ruta para ver el estado de los nodos
@app.route('/nodos', methods=['GET'])
def obtener_nodos():
    return jsonify({"nodos": list(blockchain.nodos)}), 200

#Ruta para ver el estado completo de la blockchain
@app.route('/estado', methods=['GET'])
def obtener_estado():
    try:
        #Información básica
        total_bloques = len(blockchain.cadena)
        es_valida = blockchain.validar_cadena()
        
        #Información del último bloque
        ultimo_bloque = None
        if blockchain.cadena:
            ultimo_bloque = blockchain.cadena[-1].to_dict()
        
        #Información del bloque génesis
        bloque_genesis = None
        if blockchain.cadena:
            bloque_genesis = blockchain.cadena[0].to_dict()
        
        #Estadísticas de la cadena
        estadisticas = {
            "total_bloques": total_bloques,
            "cadena_valida": es_valida,
            "nodos_registrados": len(blockchain.nodos),
            "puerto_servidor": puerto,
            "ultimo_bloque": ultimo_bloque,
            "bloque_genesis": bloque_genesis,
            "hash_cadena_completa": blockchain.cadena[-1].hash if blockchain.cadena else None
        }
        
        return jsonify(estadisticas), 200
    except Exception as e:
        return jsonify({"error": f"Error al obtener estado: {str(e)}"}), 500

#Ruta para crear un nuevo bloque (por ejemplo, una tarjeta)
@app.route('/crear_bloque', methods=['POST'])
def crear_bloque():
    datos = request.get_json()
    
    bloque = blockchain.agregar_bloque(
        datos['datos'],
        datos.get('firma', ''),  ##por ahora vacía
        datos['clave_publica']
    )
    return jsonify(bloque.to_dict()), 201



if __name__ == '__main__':
    app.run(port=puerto)