from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature

class ValidarTarjeta:
    def __init__(self):
        pass

    def reconstruir_clave_publica(self, pem_string):
        """
        Reconstruye el objeto de clave pública desde el string PEM.
        """
        return serialization.load_pem_public_key(pem_string.encode())

    def verificar_firma(self, clave_publica, datos, firma_base64):
        """
        Verifica que la firma digital sea válida para los datos dados.
        """
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

        datos = f"{numero}|{fecha}|{cvv}|{nip}"
        encontrada = False

        for bloque in blockchain.cadena:
            if bloque.index == 0:
                continue  # Saltar el bloque génesis

            datos_bloque = bloque.datos
            firma = bloque.firma
            clave_publica_pem = bloque.clave_publica

            try:
                clave_publica = self.reconstruir_clave_publica(clave_publica_pem)
                es_valido = self.verificar_firma(clave_publica, datos, firma)

                if es_valido:
                    print(f"\nTarjeta VALIDA encontrada en el bloque #{bloque.index}:")
                    print(f"Firma digital válida :)")
                    encontrada = True
                    break
                else:
                    print(f"!!!Firma no válida en el bloque #{bloque.index}")

            except Exception as e:
                print(f"!!!Error procesando el bloque #{bloque.index}: {e}")

        if not encontrada:
            print("\n!!!La tarjeta no está registrada en la blockchain o la firma no es válida")
