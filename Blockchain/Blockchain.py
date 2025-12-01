#import hashlib
from .Bloque import Block
#import time
import requests
#from datetime import datetime
import json

class Blockchain:
    def __init__(self, port):
        self.cadena = []
        self.port = port
        self.nodos = set()

        if self.port == 5000:
            self.crear_bloque_genesis()

    def agregar_nodo(self, nodo):
        self.nodos.add(nodo)

    def crear_bloque_genesis(self):
        bloque_genesis = Block(
            index=0,
            datos='Bloque Genesis',
            firma='',
            clave_publica='',
            previous_hash='0'
        )
        #calcular el hash del bloque génesis
        bloque_genesis.hash = bloque_genesis.calcular_hash()
        self.cadena.append(bloque_genesis)
        print("Bloque génesis creado con éxito.")

    def crear_bloque(self, datos, firma, clave_publica):
        index = len(self.cadena)
        previous_hash = self.cadena[-1].hash if self.cadena else "0"
        nuevo_bloque = Block(index, datos, firma, clave_publica, previous_hash)
        nuevo_bloque.hash = nuevo_bloque.calcular_hash()
        return nuevo_bloque

    def agregar_bloque(self, datos, firma, clave_publica, propagar=True):
        nuevo_bloque = self.crear_bloque(datos, firma, clave_publica)
        if nuevo_bloque.verificar_firma():
            self.cadena.append(nuevo_bloque)
            print(f"Bloque #{nuevo_bloque.index} agregado exitosamente.")
            if propagar:
                self.difundir_bloque(nuevo_bloque)
            return nuevo_bloque
        else:
            print("¡¡Firma inválida!! Bloque no agregado.")
            return None

    def difundir_bloque(self, bloque):
        for nodo in self.nodos:
            try:
                url = f"http://{nodo}/recibir_bloque"
                response = requests.post(url, json=bloque.to_dict())
                print(f"Bloque enviado a {nodo}: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Error al enviar el bloque a {nodo}: {e}")

    def validar_cadena(self):
        for i in range(1, len(self.cadena)):
            bloque_actual = self.cadena[i]
            bloque_anterior = self.cadena[i - 1]

            if bloque_actual.hash != bloque_actual.calcular_hash():
                return False
            if bloque_actual.previous_hash != bloque_anterior.hash:
                return False
            if not bloque_actual.verificar_firma():
                return False
        return True

    def mostrar_blockchain(self):
        if not self.cadena:
            print("La blockchain está vacía.")
            return

        print("\nBlockchain:")
        for bloque in self.cadena:
            print(json.dumps(bloque.to_dict(), indent=4, ensure_ascii=False))
        print("-" * 40)

    def enviar_bloque_genesis_al_nodo(self, url_nodo="http://127.0.0.1:5000"):
        try:
            respuesta = requests.get(f"{url_nodo}/blockchain")
            if respuesta.status_code == 200:
                cadena = respuesta.json().get("cadena", [])
                hashes = [bloque["hash"] for bloque in cadena]

                bloque_genesis = self.cadena[0]
                if bloque_genesis.hash not in hashes:
                    response = requests.post(f"{url_nodo}/agregar_bloque", json=bloque_genesis.to_dict())
                    if response.status_code == 200:
                        print("<<Bloque génesis enviado al nodo>>\n")
                    else:
                        print("¡¡Error!! al enviar bloque génesis:", response.json())
            else:
                print("No se pudo obtener la cadena del nodo :()")
        except requests.exceptions.RequestException as e:
            print(f"!!Error de conexión al nodo: {e}")
