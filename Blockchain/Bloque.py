import hashlib
import json
import time
import base64

from cryptography.hazmat.primitives.asymmetric import padding  
from cryptography.hazmat.primitives import hashes 
from cryptography.hazmat.primitives.serialization import load_der_public_key

class Block:
    def __init__(self, index, datos, firma, clave_publica, previous_hash=""):
        self.index = index

        # Si 'datos' viene como JSON (str), lo parseamos a dict.
        if isinstance(datos, str):
            try:
                datos = json.loads(datos)
            except json.JSONDecodeError:
                #print("⚠️ Datos inválidos en el bloque (no es JSON)")
                datos = {}
        self.datos = datos

        self.firma = firma
        self.clave_publica = clave_publica
        self.previous_hash = previous_hash
        self.hash = self.calcular_hash()

    
    def calcular_hash(self):
        # Convertir el objeto en un diccionario y luego a una cadena JSON para calcular el hash

        block_data = {
            "index": self.index,
            "datos": self.datos,
            "firma": base64.b64encode(self.firma).decode('utf-8') if isinstance(self.firma, bytes) else self.firma,
            "clave_publica": self.clave_publica.decode('utf-8') if isinstance(self.clave_publica, bytes) else self.clave_publica,
            "previous_hash": self.previous_hash
        }

        #la variable block_data contiene todos los datos del bloque, incluyendo la firma y la clave publica
        # Convertimos a JSON string, porque el hash se calcula sobre una cadena de texto y como en este caso 
        # no se puede calcular el hash sobre un objeto, entonces convertimos el objeto a una cadena de texto

        # Convertimos a JSON string
        #json.dumps() convierte un objeto de Python a una cadena JSON
        #*
        # Parametros: 
        # - block_data: el objeto que queremos convertir a JSON  
        # - sort_keys=True: ordena las claves del diccionario alfabéticamente, para que el hash sea el mismo 
        #   independientemente del orden de las claves
        # *#
        block_string = json.dumps(block_data, sort_keys=True).encode()

        # Hash usando SHA-256
        return hashlib.sha256(block_string).hexdigest()
    
    #
    def verificar_firma(self):
        return True

    

    def to_dict(self):
        return {
            'index': self.index,
            #'timestamp': self.timestamp,
            'datos': self.datos,
            'firma': self._to_str(self.firma),
            'clave_publica': self._to_str(self.clave_publica),
            'previous_hash': self.previous_hash,
            'hash': getattr(self, "hash", )
        }

    @staticmethod
    def _to_str(value):
        # Convierte bytes a str; si ya es str, lo devuelve
        if isinstance(value, (bytes, bytearray)):
            return value.decode('utf-8')
        return value


