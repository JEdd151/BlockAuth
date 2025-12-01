import os
import time
import csv
import statistics
import requests

from BD.GestorBDTarjetas import GestorBDTarjetas
from Tarjetas.TarjetasData import TarjetasData
from Cifrado.Claves import Claves
from Cifrado.FirmaDigital import FirmaDigital
from Blockchain.Blockchain import Blockchain
from Blockchain.Bloque import Block


URL_NODO = "http://127.0.0.1:5000"
RUTA_CSV = os.path.join("build", "pruebas.csv")


def sincronizar_blockchain_desde_nodo(blockchain: Blockchain) -> None:
    #Sincroniza la cadena local con la cadena del nodo Flask
    try:
        resp = requests.get(f"{URL_NODO}/cadena", timeout=10)
        if not resp.ok:
            print("No se pudo sincronizar con el servidor")
            return

        cadena_remota = resp.json()
        blockchain.cadena.clear()

        for bloque_data in cadena_remota:
            bloque = Block(
                bloque_data["index"],
                bloque_data["datos"],
                bloque_data["firma"],
                bloque_data["clave_publica"],
                bloque_data["previous_hash"],
            )
            bloque.hash = bloque_data["hash"]
            blockchain.cadena.append(bloque)

    except Exception as e:
        print(f"Error de conexión al sincronizar: {e}")


def crear_y_enviar_tarjeta(blockchain: Blockchain, gestor: GestorBDTarjetas) -> bool:
    
    #Crea una tarjeta, la inserta en la BD, genera claves y firma,
    #construye un bloque y lo envía al nodo Flask.
    #Devuelve True si el POST al nodo fue correcto, False si hubo error HTTP.
    tarjeta = TarjetasData()
    
    gestor.insertar_tarjeta(tarjeta)

    id_tarjeta = gestor.obtener_ultimo_id_tarjeta()
    claves = Claves(
        id_tarjeta,
        tarjeta.numero_tarjeta,
        tarjeta.fecha_vencimiento,
        tarjeta.cvv,
        tarjeta.nip,
    )

    #generar y guardar claves + hash
    clave_publica_pem, _ = claves.guardar_claves_txt(
        numero=tarjeta.numero_tarjeta,
        fecha=tarjeta.fecha_vencimiento,
        cvv=tarjeta.cvv,
        nip=tarjeta.nip,
    )

    #leer hash para blockchain
    ruta_hash = os.path.join("Informacion_Usuario", "hash_blockchain.txt")
    hash_tarjeta = ""
    if os.path.exists(ruta_hash):
        with open(ruta_hash, encoding="utf-8") as f:
            lineas = f.readlines()
        if len(lineas) >= 3:
            hash_tarjeta = lineas[2].strip()

    datos = {"hash_tarjeta": hash_tarjeta}

    #firmar datos
    clave_privada_pem = claves.obtener_clave_privada()
    firma_b64 = FirmaDigital.datos_firma(
        f"{tarjeta.numero_tarjeta}|{tarjeta.fecha_vencimiento}|{tarjeta.cvv}|{tarjeta.nip}",
        clave_privada_pem,
    )

    #obtener estado del nodo para index y previous_hash
    try:
        resp_estado = requests.get(f"{URL_NODO}/cadena", timeout=10)
        if resp_estado.ok:
            cadena_remota = resp_estado.json()
            if cadena_remota:
                ultimo_bloque = cadena_remota[-1]
                nuevo_index = ultimo_bloque["index"] + 1
                previous_hash = ultimo_bloque["hash"]
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

    bloque = Block(
        index=nuevo_index,
        datos=datos,
        firma=firma_b64,
        clave_publica=clave_publica_pem,
        previous_hash=previous_hash,
    )
    bloque.hash = bloque.calcular_hash()

    #agregar localmente
    blockchain.cadena.append(bloque)

    #enviar al nodo Flask
    try:
        resp = requests.post(
            f"{URL_NODO}/agregar_bloque", json=bloque.to_dict(), timeout=10
        )
        if resp.ok:
            return True
        else:
            print("Error HTTP al propagar bloque:", resp.status_code, resp.text)
            return False
    except Exception as e:
        print("Error al conectar con nodo:", e)
        return False


def asegurar_directorio_build() -> None:
    if not os.path.exists("build"):
        os.makedirs("build")


def asegurar_csv_con_cabecera() -> None:
    asegurar_directorio_build()
    if not os.path.exists(RUTA_CSV):
        with open(RUTA_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "n_registros",
                    "agregar_s_prom",
                    "agregar_s_std",
                    "verificar_s_prom",
                    "verificar_s_std",
                    "errores_http",
                    "cadena_valida",
                    "tasa_exito",
                    "tamano_cadena",
                ]
            )


def escribir_resultado_csv(
    n_registros: int,
    tiempos_agregar: list[float],
    tiempos_verificar: list[float],
    errores_http: int,
    cadena_valida: bool,
    tamano_cadena: int,
) -> None:
    asegurar_csv_con_cabecera()

    agregar_prom = statistics.mean(tiempos_agregar)
    agregar_std = statistics.pstdev(tiempos_agregar) if len(tiempos_agregar) > 1 else 0.0
    verificar_prom = statistics.mean(tiempos_verificar)
    verificar_std = (
        statistics.pstdev(tiempos_verificar) if len(tiempos_verificar) > 1 else 0.0
    )

    total_intentos = len(tiempos_agregar)
    tasa_exito = (
        1.0 - errores_http / total_intentos if total_intentos > 0 else 0.0
    )

    with open(RUTA_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                n_registros,
                agregar_prom,
                agregar_std,
                verificar_prom,
                verificar_std,
                errores_http,
                cadena_valida,
                tasa_exito,
                tamano_cadena,
            ]
        )


def main():
    print("=== Pruebas de generación y verificación de tarjetas ===")
    try:
        n_registros = int(input("Número de tarjetas por prueba (n): ").strip())
    except ValueError:
        print("Valor de n inválido.")
        return

    try:
        repeticiones = input("Número de repeticiones: ").strip()
        repeticiones = int(repeticiones) if repeticiones else 5
    except ValueError:
        print("Valor de repeticiones inválido.")
        return

    if repeticiones < 5:
        print("Usando al menos 5 repeticiones.")
        repeticiones = 5

    gestor = GestorBDTarjetas()
    blockchain = Blockchain(5000)

    tiempos_agregar: list[float] = []
    tiempos_verificar: list[float] = []
    errores_http_totales = 0

    for r in range(repeticiones):
        print(f"\n--- Repetición {r + 1}/{repeticiones} ---")

        #sincronizar antes de empezar
        sincronizar_blockchain_desde_nodo(blockchain)

        #medir tiempo de agregar n tarjetas
        errores_http = 0
        t_ini_agregar = time.perf_counter()
        for _ in range(n_registros):
            ok = crear_y_enviar_tarjeta(blockchain, gestor)
            if not ok:
                errores_http += 1
        t_fin_agregar = time.perf_counter()

        dur_agregar = (t_fin_agregar - t_ini_agregar) / max(n_registros, 1)
        tiempos_agregar.append(dur_agregar)
        errores_http_totales += errores_http
        print(f"Tiempo medio de agregado (s): {dur_agregar:.6f}  | errores_http: {errores_http}")

        #volver a sincronizar para tener la cadena actualizada completa
        sincronizar_blockchain_desde_nodo(blockchain)

        #medir tiempo de verificación de la cadena completa
        t_ini_ver = time.perf_counter()
        es_valida = blockchain.validar_cadena()
        t_fin_ver = time.perf_counter()
        dur_ver = t_fin_ver - t_ini_ver
        tiempos_verificar.append(dur_ver)

        print(
            f"Tiempo verificación cadena (s): {dur_ver:.6f}  | cadena_valida={es_valida}"
        )

    #estado final de la cadena
    sincronizar_blockchain_desde_nodo(blockchain)
    cadena_valida_final = blockchain.validar_cadena()
    tamano_cadena = len(blockchain.cadena)

    escribir_resultado_csv(
        n_registros=n_registros,
        tiempos_agregar=tiempos_agregar,
        tiempos_verificar=tiempos_verificar,
        errores_http=errores_http_totales,
        cadena_valida=cadena_valida_final,
        tamano_cadena=tamano_cadena,
    )

    gestor.cerrar_conexion()

    print("\n=== Resultado guardado en build/pruebas.csv ===")
    print(f"n_registros = {n_registros}, repeticiones = {repeticiones}")
    print(f"tamaño final de la cadena: {tamano_cadena}")


if __name__ == "__main__":
    main()


