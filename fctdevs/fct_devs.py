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
    
class IOCard():
    OK_RESULT = "OK"
    INDEX_RED = 0
    INDEX_GREEN = 1
    INDEX_BLUE = 2
    def __init__(self):

        # str that saves COM port
        self.COM_port = None

        self.io = ctypes.cdll.LoadLibrary(r".\ioportlib.dll")

        # str = io.Err()
        self.io.io_Err.restype = ctypes.c_char_p

        # io.Open("COM1")
        self.io.io_Open.restype = ctypes.c_bool
        self.io.io_Open.argtypes = [ctypes.c_char_p]

        # io.Close()
        self.io.io_Close.restype = ctypes.c_void_p

        # Res = io.dim16Val(ModuleNum,InpNum)
        self.io.io_dim16Val.restype = ctypes.c_bool
        self.io.io_dim16Val.argtypes = [ctypes.c_int, ctypes.c_int]

        # io.dom16Val(ModuleNum,OutNum,OutVal)
        
        self.io.io_dom16Val.restype = ctypes.c_void_p
        self.io.io_dom16Val.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_bool]

        # Res = io.lim16Val(ModuleNum,InpNum)
        self.io.io_lim16Val.restype = ctypes.c_bool
        self.io.io_lim16Val.argtypes = [ctypes.c_int, ctypes.c_int]

        # Res = io.rgbimVal(ModuleNum,InpNum,ColorNum)
        self.io.io_rgbimVal.restype = ctypes.c_int
        self.io.io_rgbimVal.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]

        # Res = io.Update(ModuleNam,ModuleNum)
        self.io.io_Update.restype = ctypes.c_bool
        self.io.io_Update.argtypes = [ctypes.c_char_p, ctypes.c_int]

    def set_port(self, _port:int):
            self.COM_port = _port

    def open(self):
        result = self.OK_RESULT
        if not self.io.io_Open(self.COM_port.encode('utf-8')):
            result = self.io.io_Err().decode('utf-8')
        return result
    
    def close(self):
        self.io.io_Close()
        return self.OK_RESULT
    
    def output(self,_module:int,_outCanal:int,_value:bool):
        self.io.io_dom16Val(_module,_outCanal,_value)
        result = self.io.io_Update("dom16",_module)
        if result:
            return self.OK_RESULT
        else:
            return self.io.io_Err()
        
    def input(self,_module:int,_inCanal:int):
        update_val = self.io.io_Update("dim16",_module)
        if update_val == True:
            return [self.OK_RESULT,self.io.io_dim16Val(_module,_inCanal)]
        else:
            return [self.io.io_Err(),False]
        
    def rgbim(self,_module:int,_canal:int):
        update_val = self.io.io_Update("rgbim",_module)
        if update_val == True:
            leds = [
                self.io.io_rgbimVal(_module,_canal,self.INDEX_RED),
                self.io.io_rgbimVal(_module,_canal,self.INDEX_GREEN),
                self.io.io_rgbimVal(_module,_canal,self.INDEX_BLUE)]
            
            return [self.OK_RESULT,leds]
        else:
            return [self.io.io_Err(),[-1]*3]
    
class DigitalOutputDev():
    HANDLER_DAQ = 0
    HANDLER_IOCard = 1
    OK_RESULT = IOCard.OK_RESULT
    def __init__(self,_modulo:int,_canal:int,_handler,_handlerType:int=HANDLER_DAQ):
        self.handlerType = _handlerType
        self.handler = _handler
        self.canal = _canal
        self.modulo = _modulo
    def setON(self):
        if self.handlerType == self.HANDLER_DAQ:
            self.handler.close_channel(self.canal)
            return self.OK_RESULT
        if self.handlerType == self.HANDLER_IOCard:
            return self.handler.output(self.modulo,self.canal,True)
        
    def setOFF(self):
        if self.handlerType == self.HANDLER_DAQ:
            self.handler.open_channel(self.canal)
            return self.OK_RESULT
        if self.handlerType == self.HANDLER_IOCard:
            return self.handler.output(self.modulo,self.canal,False)
        
class BlockElement(DigitalOutputDev):
    def __init__(self,_modulo:int,_canal:int,_handler,_handlerType:int=DigitalOutputDev.HANDLER_DAQ):
        super().__init__(_modulo,_canal,_handler,_handlerType)

    def block(self):
        self.setON()
    
    def unblock(self):
        self.setOFF()

class ANDON(DigitalOutputDev):
    def __init__(self,_modulo:int,_canal:int,_handler,_handlerType:int=DigitalOutputDev.HANDLER_DAQ):
        super().__init__(_modulo,_canal,_handler,_handlerType)

    def turn_on(self):
        self.setON()
    
    def turn_off(self):
        self.setOFF()

class Relay(DigitalOutputDev):
    def __init__(self,_modulo:int,_canal:int,_handler,_handlerType:int=DigitalOutputDev.HANDLER_DAQ):
        super().__init__(_modulo,_canal,_handler,_handlerType)

    def energize(self):
        self.setON()

    def deenergize(self):
        self.setOFF()

class PistonPisador(Relay):
    def __init__(self,_modulo:int,_canal:int,_handler,_handlerType:int=DigitalOutputDev.HANDLER_DAQ):
        super().__init__(_modulo,_canal,_handler,_handlerType)

class PistonPines(Relay):
    def __init__(self,_modulo:int,_canal:int,_handler,_handlerType:int=DigitalOutputDev.HANDLER_DAQ):
        super().__init__(_modulo,_canal,_handler,_handlerType)

class PistonPinesProg(Relay):
    def __init__(self,_modulo:int,_canal:int,_handler,_handlerType:int=DigitalOutputDev.HANDLER_DAQ):
        super().__init__(_modulo,_canal,_handler,_handlerType)

class DigitalInputDev():
    HANDLER_DAQ = 0
    HANDLER_IOCard = 1
    OK_RESULT = IOCard.OK_RESULT
    NOT_DEV = "NOT_DEV"
    def __init__(self,_modulo:int,_canal:int,_handler,_handlerType:int=HANDLER_IOCard):
        self.handlerType = _handlerType
        self.handler = _handler
        self.canal = _canal
        self.modulo = _modulo

    def getState(self):
        if self.handlerType == self.HANDLER_IOCard:
            return self.handler.input(self.modulo,self.canal)
        else:
            return [self.NOT_DEV,False]
        
class BoardDetect(DigitalInputDev):
    def __init__(self, _modulo:int, _canal:int, _handler, _handlerType = DigitalInputDev.HANDLER_IOCard):
        super().__init__(_modulo, _canal, _handler, _handlerType)

    def isDetected(self):
        return self.getState()
    
class PCBDetect(BoardDetect):
    def __init__(self, _modulo:int, _canal:int, _handler, _handlerType = DigitalInputDev.HANDLER_IOCard):
        super().__init__(_modulo, _canal, _handler, _handlerType)