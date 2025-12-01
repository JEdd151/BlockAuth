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
    blockchain = Blockchain(5000)  ##crea génesis si es nodo 5000
    validador = ValidarTarjeta()

    while True:
        print("\n=== Menú Principal ===")
        print("1. Mostrar Blockchain")
        print("2. Crear nueva tarjeta")
        print("3. Validar Tarjeta")
        print("4. Salir")
        opcion = input("Elige una opción: ")

        if opcion == "1":
            #sincronizar con el servidor antes de mostrar
            try:
                resp = requests.get("http://127.0.0.1:5000/cadena")
                if resp.ok:
                    cadena_remota = resp.json()
                    blockchain.cadena.clear()
                    for bloque_data in cadena_remota:
                        #recrear bloques desde los datos remotos
                        from Blockchain.Bloque import Block
                        bloque = Block(
                            bloque_data['index'],
                            bloque_data['datos'],
                            bloque_data['firma'],
                            bloque_data['clave_publica'],
                            bloque_data['previous_hash']
                        )
                        bloque.hash = bloque_data['hash']
                        blockchain.cadena.append(bloque)
                    print("✓ Cadena sincronizada con el servidor")
                else:
                    print("No se pudo sincronizar con el servidor")
            except Exception as e:
                print(f"Error de conexión: {e}")
            
            blockchain.mostrar_blockchain()

        elif opcion == "2":
            tarjeta = TarjetasData()
            gestor.insertar_tarjeta(tarjeta)
            print(f"\n--Tarjeta creada:--\n{tarjeta}\n")

            id_tarjeta = gestor.obtener_ultimo_id_tarjeta()
            claves = Claves(id_tarjeta, tarjeta.numero_tarjeta,
                            tarjeta.fecha_vencimiento, tarjeta.cvv, tarjeta.nip)

            #desempaquetar solo la clave pública
            clave_publica_pem, hash_tarjeta = claves.guardar_claves_txt(
                numero=tarjeta.numero_tarjeta,
                fecha=tarjeta.fecha_vencimiento,
                cvv=tarjeta.cvv,
                nip=tarjeta.nip
            )
            print("--Claves generadas y guardadas correctamente--\n")

            #leer hash
            ruta_hash = os.path.join("Informacion_Usuario", "hash_blockchain.txt")
            hash_tarjeta = ""
            if os.path.exists(ruta_hash):
                with open(ruta_hash) as f:
                    lineas = f.readlines()
                if len(lineas) >= 3:
                    hash_tarjeta = lineas[2].strip()
                print(f"---Hash leído desde archivo: {hash_tarjeta}")

            datos = { 'hash_tarjeta': hash_tarjeta }

            #firmar los datos con la clave privada
            clave_privada_pem = claves.obtener_clave_privada()  # Obtén la clave privada
            firma_b64 = FirmaDigital.datos_firma(f"{tarjeta.numero_tarjeta}|{tarjeta.fecha_vencimiento}|{tarjeta.cvv}|{tarjeta.nip}", clave_privada_pem)
            
            #obtener estado actual del servidor para usar el índice correcto
            try:
                resp_estado = requests.get("http://127.0.0.1:5000/cadena")
                if resp_estado.ok:
                    cadena_remota = resp_estado.json()
                    if cadena_remota:
                        ultimo_bloque = cadena_remota[-1]
                        nuevo_index = ultimo_bloque['index'] + 1
                        previous_hash = ultimo_bloque['hash']
                    else:
                        nuevo_index = 1
                        previous_hash = "0"
                else:
                    nuevo_index = 1
                    previous_hash = "0"
            except Exception as e:
                print(f"Error obteniendo estado del servidor: {e}")
                nuevo_index = 1
                previous_hash = "0"

            #crear bloque con el índice correcto
            from Blockchain.Bloque import Block
            bloque = Block(
                index=nuevo_index,
                datos=datos,
                firma=firma_b64,
                clave_publica=clave_publica_pem,
                previous_hash=previous_hash
            )
            bloque.hash = bloque.calcular_hash()

            #agregar a la cadena local
            blockchain.cadena.append(bloque)
            print(f"Bloque #{bloque.index} creado localmente")

            #propagar al servidor
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

        elif opcion == "3":
            #sincronizar con el servidor antes de validar
            try:
                resp = requests.get("http://127.0.0.1:5000/cadena")
                if resp.ok:
                    cadena_remota = resp.json()
                    blockchain.cadena.clear()
                    for bloque_data in cadena_remota:
                        from Blockchain.Bloque import Block
                        bloque = Block(
                            bloque_data['index'],
                            bloque_data['datos'],
                            bloque_data['firma'],
                            bloque_data['clave_publica'],
                            bloque_data['previous_hash']
                        )
                        bloque.hash = bloque_data['hash']
                        blockchain.cadena.append(bloque)
                    print("Cadena sincronizada para validación")
                else:
                    print("No se pudo sincronizar con el servidor")
            except Exception as e:
                print(f"Error de conexión: {e}")
            
            validador.validar_tarjeta(blockchain)
            print("Proceso de validacion exitoso.\n")

        elif opcion == "4":
            break
        else:
            print("¡¡Opción inválida!!")

    gestor.cerrar_conexion()


if __name__ == '__main__':
    main()
