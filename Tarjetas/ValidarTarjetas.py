from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature

class ValidarTarjeta:
    def __init__(self):
        pass

    def reconstruir_clave_publica(self, pem_string):
        return serialization.load_pem_public_key(pem_string.encode())

    def verificar_firma(self, clave_publica, datos, firma_base64):
        import base64
        firma_bytes = base64.b64decode(firma_base64)
        datos_bytes = datos.encode()

        try:
            clave_publica.verify(
                firma_bytes,
                datos_bytes,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False

    def validar_tarjeta(self, blockchain):
        print("\n=== Validación de Tarjeta con Firma Digital ===")
        numero = input("Número de tarjeta: ")
        fecha = input("Fecha de vencimiento (MM/AA): ")
        cvv = input("CVV: ")
        nip = input("NIP: ")

        datos_tarjeta = f"{numero}|{fecha}|{cvv}|{nip}"
        encontrada = False

        print(f"\nBuscando tarjeta en {len(blockchain.cadena)} bloques...")

        for bloque in blockchain.cadena:
            if bloque.index == 0:
                continue  ##saltar el bloque génesis

            firma = bloque.firma
            clave_publica_pem = bloque.clave_publica

            try:
                clave_publica = self.reconstruir_clave_publica(clave_publica_pem)
                es_valido = self.verificar_firma(clave_publica, datos_tarjeta, firma)

                if es_valido:
                    print(f"\nTarjeta VALIDA encontrada en el bloque #{bloque.index}")
                    print(f"Firma digital válida")
                    print(f"Datos del bloque: {bloque.datos}")
                    encontrada = True
                    break
                else:
                    print(f"- Bloque #{bloque.index}: Firma no coincide")

            except Exception as e:
                print(f"- Bloque #{bloque.index}: Error - {e}")

        if not encontrada:
            print(f"\nLa tarjeta {numero} no está registrada en la blockchain")
            print("Verifica que los datos ingresados sean correctos")
