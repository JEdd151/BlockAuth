import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

class FirmaDigital:

    #Este metodo genera la firma digital de los datos
    #Recibe los datos y la clave privada en formato PEM
    @staticmethod
    def datos_firma(datos: str, clave_privada_pem) -> str:
        #Acepta str o bytes para la clave privada
        if isinstance(clave_privada_pem, str):
            #si la clave privada es un string, la convertimos a bytes
            clave_bytes = clave_privada_pem.encode('utf-8')
        else:
            #si no es un string, la dejamos como bytes
            clave_bytes = clave_privada_pem

        #se carga la clave privada

        clave_privada = serialization.load_pem_private_key(#permite cargar la clave privada en formato PEM
            clave_bytes,
            password=None #esta es la contraseña de la clave privada, si no tiene contraseña se pone None
        )

        #se firma los datos con la clave privada y se codifica a base64
        firma = clave_privada.sign(
            datos.encode('utf-8'), #convierte los datos a bytes
            padding.PKCS1v15(), ##se usa el padding PKCS1v15 porque es el mas comun para RSA
            hashes.SHA256()
        )

        #se codifica la firma a base64 para poder guardarla o mostrarla
        return base64.b64encode(firma).decode('utf-8')
    

    #Este metodo verifica la firma digital es valida para un conjunto 
    #de datos utilzando la clave publica asociada al bloque
    #Recibe los datos, la firma y la clave publica en formato PEM
    @staticmethod
    def verificar_firma(datos: str, firma_b64: str, clave_publica_pem: str) -> bool:
        firma = base64.b64decode(firma_b64)
        #se carga la clave publica y se convierte a bytes
        clave_publica = serialization.load_pem_public_key(
            clave_publica_pem.encode('utf-8')
        )
        #se verifica la firma con la clave publica y se decodifica a bytes
        #si la firma es valida, no se lanza ninguna excepcion y se regresa True
        #si la firma no es valida, se lanza una excepcion y se regresa False
        try:
            clave_publica.verify(
                firma,
                datos.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
