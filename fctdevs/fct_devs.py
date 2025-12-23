import serial
import time as t
import ctypes
import pyvisa

class DAQ():
    def __init__(self, _rm:pyvisa.ResourceManager, _resource_name:str):
        self.instrument = _rm.open_resource(_resource_name,access_mode=1,open_timeout=3000)
            

    def open_channel(self, _channel:int):
        self.instrument.write(f'ROUT:OPEN (@{_channel})')

    def close_channel(self, _channel:int):
        self.instrument.write(f'ROUT:CLOSE (@{_channel})')

    def measure_resistance(self, _channel:int, _ohm_range:int =100000, _resolution:float =0.03):
        resistance = self.instrument.query(f'MEAS:RES? {_ohm_range},{_resolution}, (@{_channel})')
        return float(resistance)
    
    def measure_voltage(self, _channel:int, _voltage_range:int=10):
        voltage = self.instrument.query(f'MEAS:VOLT:DC? {_voltage_range},(@{_channel})')
        return float(voltage)

    def close(self):
        self.instrument.close()

class PowerSource():
    def __init__(self, _rm:pyvisa.ResourceManager, resource_name:str):
        self.instrument = _rm.open_resource(resource_name,access_mode=1,open_timeout=3000)

    def set_voltage(self, _voltage:float, _channel:str='CH1'):
        self.instrument.write(f':{_channel}:VOLTage {_voltage}')

    def set_current(self, _current:float, _channel:str='CH1'):
        self.instrument.write(f':{_channel}:CURRent {_current}')

    def on(self,_channel:str='CH1'):
        self.instrument.write(f'OUTPut {_channel},ON')

    def off(self,_channel:str='CH1'):
        self.instrument.write(f'OUTPut {_channel},OFF')

    def measure_voltage(self,_channel:str='CH1'):
        return float(self.instrument.query(f'MEAS:VOLT? {_channel}'))

    def measure_current(self,_channel:str='CH1'):
        return float(self.instrument.query(f'MEAS:CURR? {_channel}'))    
    def close(self):
        self.instrument.close()

class BlockElement():
    def __init__(self, _canal:int, _daq:DAQ):
        self.canal = _canal
        self.daq = _daq

    def block(self):
        self.daq.close_channel(self.canal)
    
    def unblock(self):
        self.daq.open_channel(self.canal)

class ANDON():
    def __init__(self,_canal:int,_daq:DAQ):
        self.canal = _canal
        self.daq = _daq

    def turn_on(self):
        self.daq.close_channel(self.canal)

    def turn_off(self):
        self.daq.open_channel(self.canal)

class Relay():
    def __init__(self,_canal:int,_daq:DAQ):
        self.canal = _canal
        self.daq = _daq

    def open(self):
        self.daq.open_channel(self.canal)

    def close(self):
        self.daq.close_channel(self.canal)

class Cover():
    def __init__(self,_canal:int,_daq:DAQ):
        self.canal = _canal
        self.daq = _daq
    
    def is_closed(self):
        try:
            resistance = self.daq.measure_resistance(self.canal)
        except:
            resistance = 999999
        finally:
            return resistance < 500

class Scanner():
    def __init__(self, _port:str):
        self.port = _port

    def set_port(self, _port:str):
        self.port = _port

    def scan_serial_HW(self, _baudrate:int=115200, _timeout:int=3,_serial_len:int = 21):
        if self.port is None:
            raise ValueError("COM port not set. Please set the COM port before scanning.")
        try:
            with serial.Serial(port=self.port, baudrate=_baudrate, timeout=_timeout) as ser:
                ser.write(b'T\r\n')
                t.sleep(1)
                serialpcb = ser.read(_serial_len)
                if not serialpcb:
                    return None
                return serialpcb.decode("utf-8")
        except(serial.SerialException,UnicodeDecodeError):
            return None

        return serialpcb
    
    def scan_serial_trigger(self, _daq:DAQ):
        if self.port is None:
            raise ValueError("COM port not set. Please set the COM port before scanning.")
        _daq.write(f'ROUT:CLOSE (@{int(self.port)})')
        t.sleep(1)
        _daq.write(f'ROUT:OPEN (@{int(self.port)})')

class FEASA():
    def __init__(self, _buffer_size:int=32, _port:int=4,_timeout:int=8000,_baudrate:bytes=b'57600'):
        self.buffer = ctypes.create_string_buffer(_buffer_size)
        self.port = _port
        self.baudrate = _baudrate
        FeasaDLL = ctypes.WinDLL('feasacom64.dll')
        self.FeasaCom_Open = FeasaDLL['FeasaCom_Open']
        self.FeasaCom_Open.argtypes = [ctypes.c_int, ctypes.c_char_p]
        self.FeasaCom_Open.restype = ctypes.c_int
        self.FeasaCom_Close = FeasaDLL['FeasaCom_Close']
        self.FeasaCom_Close.argtypes = [ctypes.c_int]
        self.FeasaCom_Close.restype = ctypes.c_int
        self.FeasaCom_Send = FeasaDLL['FeasaCom_Send']
        self.FeasaCom_Send.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p]
        self.FeasaCom_Send.restype = ctypes.c_int
        self.FeasaCom_EnumPorts = FeasaDLL['FeasaCom_EnumPorts']
        self.FeasaCom_EnumPorts.restype = ctypes.c_int
        self.FeasaCom_SetResponseTimeout = FeasaDLL['FeasaCom_SetResponseTimeout']
        self.FeasaCom_SetResponseTimeout.argtypes = [ctypes.c_uint]
        self.FeasaCom_SetResponseTimeout.restype = ctypes.c_int
        self.FeasaCom_SetResponseTimeout(_timeout)
    
    def set_port(self, _port:int):
        self.port = _port

    def set_baudrate(self, _baudrate:bytes):
        self.baudrate = _baudrate

    def open(self):
        result = self.FeasaCom_Open(self.port, self.baudrate)
        if result != 0:
            return False
        return True
    
    def get_rgb(self, _fiber:int):
        command = b'Getrgbi' + b'%02d'%_fiber
        ret = self.FeasaCom_Send(self.port,b'Capture',self.buffer)
        ret = self.FeasaCom_Send(self.port,command,self.buffer)
        if ret == 1:
            led = self.buffer.value.decode()
            segments = led.split(" ")
            return float(segments[0]),float(segments[1]),float(segments[2])
        else:
            return None
        
    def get_rgbs(self, _fibers:list):
        result = []
        for _fiber in _fibers:
            tmp = self.get_rgb(_fiber)
            if tmp == None:
                return None
            else:
                result.append(tmp)
        return result
    
    def close(self):
        result = self.FeasaCom_Close(self.port)
        if result != 0:
            return False
        return True
    

    
