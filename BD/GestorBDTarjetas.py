import sqlite3
from Tarjetas.TarjetasData import TarjetasData

class GestorBDTarjetas:
    def __init__(self, db_name = "Blockchain.db"):
        self.db_name = db_name
        self.conexion = sqlite3.connect(self.db_name)
        self.cursor = self.conexion.cursor()
        self.crear_tabla()

    def crear_tabla(self):
        #el tipo TEXT es un string, este para que no haya problemas con los datos.
        #porque no INTEGER? porque el numero de tarjeta puede empezar con 0 y si se guarda como INTEGER se pierde el 0
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Tarjetas(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_tarjeta TEXT NOT NULL,
                fecha_vencimiento TEXT NOT NULL,
                cvv TEXT NOT NULL,
                nip INTEGER UNIQUE NOT NULL
            )
        ''')
        self.conexion.commit() #hacemos commit para que se guarden los cambios en la base de datos
            
    def insertar_tarjeta(self, tarjeta: TarjetasData):
        try:
            self.cursor.execute('''
                INSERT INTO Tarjetas(numero_tarjeta, fecha_vencimiento, cvv, nip)
                VALUES(?,?,?,?)
            ''',
                (tarjeta.numero_tarjeta, tarjeta.fecha_vencimiento, tarjeta.cvv, tarjeta.nip)
            )
            self.conexion.commit()
        except sqlite3.IntegrityError as e:
            print(f"!!!Error al insertar la tarjeta: {e}")

            
    def obtener_tarjetas(self):
        self.cursor.execute('''
            SELECT * FROM Tarjetas
        ''')
        return self.cursor.fetchall() #fetchall() regresa una lista con todas las filas de la tabla
    
    def obtener_tarjeta_por_nip(self, id_nip):
        self.cursor.execute('''
            SELECT * FROM Tarjetas WHERE nip = ?
        ''',
            (id_nip,)
        )
        tarjeta_data = self.cursor.fetchone()
        if tarjeta_data:
            #*tarjeta_data es para desempaquetar la tupla
            #si no se pone el *tarjeta_data, se regresaria una tupla con los datos de la tarjeta
            #y no un objeto de tipo TarjetasData
            return tarjeta_data
        else:
            return None
    
    def obtener_ultimo_id_tarjeta(self):
        try:
            self.cursor.execute("SELECT MAX(id) FROM Tarjetas")

            resultado = self.cursor.fetchone()
            return resultado[0] if resultado and resultado [0] else None
        except Exception as e:
            print(f"!!!Error al obtener el último ID de tarjeta: {e}")
            return None
    
    def cerrar_conexion(self):
        self.conexion.close()
        
    def borrar_tabla(self):
        self.cursor.execute('''
            DROP TABLE IF EXISTS Tarjetas
        ''')
        self.conexion.commit()
    

if __name__ == '__main__':
    from BD.GestorBDTarjetas import GestorBDTarjetas

    #Crear instancia del gestor
    gestor = GestorBDTarjetas()

    #Borrar la tabla
    gestor.borrar_tabla()

    #Cerrar conexión
    gestor.cerrar_conexion()

    print("Tabla 'Tarjetas' borrada exitosamente.")

