# Sistema Blockchain para Gestión de Tarjetas

Este proyecto implementa un sistema basado en blockchain para la gestión de tarjetas, incluyendo la creación, validacion y firma digital de datos.
El sistema utiliza criptografía para garantizar la seguridad e integridad de la información.

## Requisitos
Antes de compilar y ejecutar el sistema, asegúrate de cumplir con los siguientes requisitos:

#### 1. Requisitos del sistema
- **Python 3.8 o superior**.

#### 2.Dependencias de Python
Las dependencias necesarias están listadas en el archivo [requirements.txt](./requirements.txt). 
Puedes instalarlas fácilmente siguiendo las instrucciones a continuacion.

## Instalación

#### 1. Clonar el repositorio
Clona el repositorio en tu máquina local:

```bash
git clone https://github.com/JEdd151/BlockAuth.git
cd BlockAuth
```

#### 2. Crear un entorno virtual
Crea y activa un entorno virtual para aislar las dependencias del proyecto:

 ```
#Crear el entorno virtual
python -m venv env

#Activar el entorno virtual
#En Windows:
env\Scripts\activate
#En macOS/Linux:
source env/bin/activate
```

#### 3.Instalar dependencias
Instalar las dependencias necesarias utilizando el archivo [requirements.txt](./requirements.txt):
```
pip install -r requirements.txt
```

## Ejecución del sistema

#### 1. Iniciar el programa
Ejecuta el archivo principal [main.py](./main.py) 

#### 2. Menú pricipal
Al ejecutrar el programa, se mostrará un menú con las siguientes opciones:

  - **Mostrar Blockchain:** Muestra todos los bloques almacenados en la blockchain, incluyendo los datos y las firmas digitales.
  - **Crear nueva tarjeta:** Genera una nueva tarjeta, crea claves públicas y privadas, firma los datos y los almacena en un bloque
    de la blockchain.
  - **Validar Tarjeta:** Valida una tarjeta verificando su firma digital y los datos almacenados en la blockchain. 
  - **Salir:** Cierra el programa.

#### 3. Iniciar nodos
El sistema permite la ejecución de múltiples nodos para simular una red blockchain. A continuacion, se describe cómo iniciar
tres nodos en diferentes puertos:

- **Nodo 1, 2 y 3**
Ejecuta los siguiente comando cada uno en diferentes terminales para iniciar los nodos en sus respectivos puertos:
```
flask run --host=127.0.0.1 --port=5000
flask run --host=127.0.0.1 --port=5001
flask run --host=127.0.0.1 --port=5002
```

#### 4. Agregar nodos vecinos
Para que los nodos se comuniquen entre sí, debes agregarlos como vecinos. Usa los siguientes comandos curl desde alguna
herramienta como Postman para interactuar con el sistema y para configurar la red:

- **Desde el nodo 1 (puerto 5000)** agregamos los nodos 2 y 3 como vecinos
```
curl -X POST -H "Content-Type: application/json" -d '{"nodo": "http://127.0.0.1:5001"}' http://127.0.0.1:5000/agregar_nodo
curl -X POST -H "Content-Type: application/json" -d '{"nodo": "http://127.0.0.1:5002"}' http://127.0.0.1:5000/agregar_nodo
```

- **Desde el nodo 2 (puerto 5000)** agregamos los nodos 1 y 3 como vecinos
```
curl -X POST -H "Content-Type: application/json" -d '{"nodo": "http://127.0.0.1:5000"}' http://127.0.0.1:5001/agregar_nodo
curl -X POST -H "Content-Type: application/json" -d '{"nodo": "http://127.0.0.1:5002"}' http://127.0.0.1:5001/agregar_nodo
```

- **Desde el nodo 2 (puerto 5000)** agregamos los nodos 1 y 3 como vecinos
```
curl -X POST -H "Content-Type: application/json" -d '{"nodo": "http://127.0.0.1:5000"}' http://127.0.0.1:5002/agregar_nodo
curl -X POST -H "Content-Type: application/json" -d '{"nodo": "http://127.0.0.1:5001"}' http://127.0.0.1:5002/agregar_nodo
```

#### 5. Sincronizar nodos
Una vez los nodos están conectados, puedes sincronizar sus cadenas de bloques con el nodo principal (puerto 5000). Usando los siguientes comandos:
```
curl -X GET http://127.0.0.1:5000/sincronizar
curl -X GET http://127.0.0.1:5001/sincronizar
curl -X GET http://127.0.0.1:5002/sincronizar
```

## Uso del sistema
Con ayuda de herramientas como postman interactuamos con el sistema. A continuación, se describem las rutas principales disponibles:

**Agregar un nodo vecino**
- **Ruta: ``` POST /agregar_nodo ```**
- **Descripción:** Agregar un nodo vecino a la red.
- **Cuerpo de la solicitud:**
```js
  {
    "nodo": "http://127.0.0.1:5001"
  }
  ```
- **Respuesta:**
```js
  {
    "mensaje": "Nodo http://127.0.0.1:5001 agregado"
  }
```

**Obtener la cadena de bloques**
- **Ruta: ``` GET /cadena ```**
- **Descripción:** Devuelve la cadena de bloques completa.
 
**Sincronizar con el nodo principal**
- **Ruta: ``` GET /sincronizar ```**
- **Descripción:** Sincroniza la cadena de bloques con el nodo principal.

## Detalles
**Firma Digital**
- Se utiliza el algoritmo RSA con un tamaño de clave de 2048 bits.
- Los datos de la tarjeta se firman con la clave privada y se verifican con la clave pública.

**Blockchain**
- Cada bloque contiene:
  - Datos de la tarjeta (hash).
  - Firma digital.
  - Clave pública
- Los bloques se encadenan para garantizar la integridad de los datos.

**Archivos Generados**
- `clave_privada.pem`: Contiene la clave privada en formato PEM.
- `clave_publica.pem`: Contiene la clave publica en formato PEM.
- `datos_tarjeta.txt`: Contiene los datos de la tarjeta y su versión cifrada.
- `hash_blockchain.txt`: Contiene el SHA-256 de los datos de la tarjeta.

## Notas Importantes
1- **Seguridad**:
  - Asegúrate de proteger los archivos que contienen las claves privadas (`clave_privada.pem`), ya que su exposición
    comprometería la seguridad del sistema.
2- **Propagación de Bloques**:
    - El programa intenta propagar los bloques a un nodo en `http://127.0.0.1:5000/agregar_bloque`.
      Asegurate de que el nodo esté en ejecución.
