from datetime import datetime
import os

class logFile():
    def __init__(self,_ruta,_nombreArchivo,_header):
        self.ruta = _ruta
        self.nombreArchivo = _nombreArchivo + " " + datetime.now().strftime("%Y-%m-%d") + ".csv"
        self.header = _header
        self.numeroElementos = len(self.header)
        if not self.buscarLogFile():
            self.fh = open(self.ruta+"/"+self.nombreArchivo,"w")
            self.crearHeader()
            self.cerrar()
            
    def buscarLogFile(self):
        if self.nombreArchivo in os.listdir(self.ruta):
            print("Ya existe un registro el dia de hoy")
            return True
        else:
            print("Creando un nuevo registro el dia de hoy")
            return False
    def crearHeader(self):
        for i in range(0,self.numeroElementos):
            if i == self.numeroElementos - 1:
                self.fh.write(f"{self.header[i]}\n")
            else:
                self.fh.write(f"{self.header[i]}\t")   
                
    def escribirLog(self,_log):
        self.fh = open(self.ruta+"/"+self.nombreArchivo,"a")
        if len(_log) == self.numeroElementos:
            for i in range(0,self.numeroElementos):
                if i == self.numeroElementos - 1:
                    self.fh.write(f"{_log[i]}\n")
                else:
                    self.fh.write(f"{_log[i]}\t")
        else:
            print("El log a escribir no coincide con el número de elementos")
        self.cerrar()
                
    def cerrar(self):
        self.fh.close()