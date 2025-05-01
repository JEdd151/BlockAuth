import os
import json
import requests
from Tarjetas.TarjetasData import TarjetasData
from BD.GestorBDTarjetas import GestorBDTarjetas
from Cifrado.Claves import Claves
from Blockchain.Blockchain import Blockchain
from Tarjetas.ValidarTarjetas import ValidarTarjeta
from Cifrado.FirmaDigital import FirmaDigital


def main():
    gestor = GestorBDTarjetas()
    blockchain = Blockchain(5000)  # Crea génesis si es nodo 5000
    validador = ValidarTarjeta()

    while True:
        print("\n=== Menú Principal ===")
        print("1. Mostrar Blockchain")
        print("2. Crear nueva tarjeta")
        print("3. Validar Tarjeta")
        print("4. Salir")
        opcion = input("Elige una opción: ")

        if opcion == "1":
            blockchain.mostrar_blockchain()

        elif opcion == "2":
            tarjeta = TarjetasData()
            gestor.insertar_tarjeta(tarjeta)
            print(f"\n--Tarjeta creada:--\n{tarjeta}\n")

            id_tarjeta = gestor.obtener_ultimo_id_tarjeta()
            claves = Claves(id_tarjeta, tarjeta.numero_tarjeta,
                            tarjeta.fecha_vencimiento, tarjeta.cvv, tarjeta.nip)

            # Desempaquetar solo la clave pública
            clave_publica_pem, hash_tarjeta = claves.guardar_claves_txt(
                numero=tarjeta.numero_tarjeta,
                fecha=tarjeta.fecha_vencimiento,
                cvv=tarjeta.cvv,
                nip=tarjeta.nip
            )
            print("--Claves generadas y guardadas correctamente--\n")

            # Leer hash
            ruta_hash = os.path.join("Informacion_Usuario", "hash_blockchain.txt")
            hash_tarjeta = ""
            if os.path.exists(ruta_hash):
                with open(ruta_hash) as f:
                    lineas = f.readlines()
                if len(lineas) >= 3:
                    hash_tarjeta = lineas[2].strip()
                print(f"---Hash leído desde archivo: {hash_tarjeta}")

            datos = { 'hash_tarjeta': hash_tarjeta }

            # Firmar los datos con la clave privada
            clave_privada_pem = claves.obtener_clave_privada()  # Obtén la clave privada
            firma_b64 = FirmaDigital.datos_firma(f"{tarjeta.numero_tarjeta}|{tarjeta.fecha_vencimiento}|{tarjeta.cvv}|{tarjeta.nip}", clave_privada_pem)
            
            # Crear y propagar bloque con la firma
            bloque = blockchain.agregar_bloque(
                datos=datos,
                firma=firma_b64,  # Firma digital
                clave_publica=clave_publica_pem
            )

            if bloque:
                bloque_payload = bloque.to_dict()
                try:
                    resp = requests.post("http://127.0.0.1:5000/agregar_bloque", json=bloque_payload)
                    if resp.ok:
                        print("<<<Bloque propagado exitosamente al nodo>>>")
                        print("=== Bloque agregado ===")
                        print(json.dumps(bloque_payload, indent=4, ensure_ascii=False))
                    else:
                        print("¡¡Error¡¡ al propagar bloque:", resp.text)
                except Exception as e:
                    print("¡¡Error!! al conectar con nodo:", e)
            else:
                print("No se pudo agregar el bloque :(")

        elif opcion == "3":
            validador.validar_tarjeta(blockchain)
            print("Proceso de validacion exitoso.\n")

        elif opcion == "4":
            break
        else:
            print("¡¡Opción inválida!!")

    gestor.cerrar_conexion()


if __name__ == '__main__':
    main()
