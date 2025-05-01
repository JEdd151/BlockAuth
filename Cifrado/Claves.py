import os 
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from Tarjetas.TarjetasData import TarjetasData
from Cifrado.Cifrar_info import Cifrado


class Claves:
    def __init__(self, usuario_id, numero, fecha, cvv, nip, carpeta_salida="Informacion_Usuario"):
        self.usuario_id = usuario_id
        self.carpeta_salida = carpeta_salida

        self.clave_privada, self.clave_publica = self.generar_claves()
        self.tarjeta = TarjetasData()

    def generar_claves(self):   
        clave_privada = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        clave_publica = clave_privada.public_key()
        return clave_privada, clave_publica

    def obtener_clave_privada(self):
        return self.clave_privada.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

    def obtener_clave_publica(self):
        return self.clave_publica.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def guardar_claves_txt(self, id=None, numero=None, fecha=None, cvv=None, nip=None):
        # 1. Generamos las claves
        self.clave_privada, self.clave_publica = self.generar_claves()

        # 2. Creamos el objeto de cifrado
        cifrado = Cifrado(self.clave_publica)

        datos_tarjeta = {
            "numero": numero,
            "fecha": fecha,
            "cvv": cvv,
            "nip": nip
        }

        # 3. Procesamos el cifrado y hash
        cifrado_b64, hash_sha256 = cifrado.dobleProceso(datos_tarjeta)

        # 4. Creamos la carpeta si no existe
        if not os.path.exists(self.carpeta_salida):
            os.makedirs(self.carpeta_salida)

        # === Archivos ===

        # Clave privada (modo binario)
        ruta_privada = os.path.join(self.carpeta_salida, "clave_privada.pem")
        with open(ruta_privada, "wb") as archivo_priv:
            archivo_priv.write(self.obtener_clave_privada())

        # Clave pública (modo binario)
        ruta_publica = os.path.join(self.carpeta_salida, "clave_publica.pem")
        with open(ruta_publica, "wb") as archivo_pub:
            archivo_pub.write(self.obtener_clave_publica())

        # Datos de la tarjeta (texto)
        ruta_datos = os.path.join(self.carpeta_salida, "datos_tarjeta.txt")
        with open(ruta_datos, "w") as archivo_datos:
            contenido = f"""
            === Datos de la Tarjeta ===
            ID: {id}
            Número: {numero}
            Fecha: {fecha}
            CVV: {cvv}
            NIP: {nip}

            === Datos Cifrados (base64) ===
            {cifrado_b64}
            """
            archivo_datos.write(contenido.strip())

        # Hash para blockchain (texto)
        ruta_hash = os.path.join(self.carpeta_salida, "hash_blockchain.txt")
        with open(ruta_hash, "w") as archivo_hash:
            archivo_hash.write(f"ID: {id}\nHASH SHA-256:\n{hash_sha256}")

        print(f"Archivos guardados en: {self.carpeta_salida}")
        return self.obtener_clave_publica().decode('utf-8'), hash_sha256
