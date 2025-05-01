import random
from datetime import datetime, timedelta

class TarjetasData:
    def __init__(self):
        self.numero_tarjeta = self.generar_numero_tarjeta()
        self.fecha_vencimiento = self.generar_fecha_vencimiento()
        self.cvv = self.generar_cvv()
        self.nip = self.generar_nip()
        
    def __str__(self):
        return f"Numero de tarjeta: {self.numero_tarjeta}\nFecha de vencimiento: {self.fecha_vencimiento}\nCVV: {self.cvv}\nNIP: {self.nip}"
    
    @staticmethod
    def generar_numero_tarjeta():
        numero_por_defecto = "400000"
        numero_tarjeta = numero_por_defecto + ''.join([str(random.randint(0, 9)) for _ in range(10)])
        return numero_tarjeta

    @staticmethod
    def generar_fecha_vencimiento():
        fecha_actual = datetime.now()
        fecha_vencimiento = fecha_actual + timedelta(days=365)#fecha actual + 1 año
        return fecha_vencimiento.strftime("%m/%y")
    
    @staticmethod
    def generar_cvv():
        return ''.join([str(random.randint(0, 9)) for _ in range(3)])
    
    @staticmethod
    def generar_nip():
        return ''.join([str(random.randint(0, 9)) for _ in range(4)])