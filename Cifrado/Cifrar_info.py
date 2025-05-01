import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import hashlib

class Cifrado:
    def __init__(self, clave_publica):
        self.clave_publica = clave_publica

    def cifrar_con_clave_publica(self, datos):
        """
        Cifra los datos usando la clave privada (firma digital simulada).
        Retorna los datos cifrados en base64.
        """
        datos_bytes = str(datos).encode('utf-8')

        datos_cifrados = self.clave_publica.encrypt(
            datos_bytes,
            padding.OAEP( 
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        #Codificamos a base64 para poder guardarlo o mostrarlo
        return datos_cifrados
    
    def generar_sha256 (self, datos):
        """"
        Generar un hash sha-256 a partir de los datos"
        """
        return hashlib.sha256(datos).hexdigest()
    
    def dobleProceso(self, datos):
        cifrado = self.cifrar_con_clave_publica(datos)
        hash_sha = self.generar_sha256(cifrado)
        return cifrado, hash_sha