from numpy import log10,floor,ceil,sign
import re
from tinyrpc.dispatch import public

etx = '\x03'
cr = '\x0D'
lf = '\x0A'
enq = '\x05'
ack = '\x06'
nak = '\x15'

def _formatFloatValue(value):
    if value == 0:
        return 0
    
    expSign = sign(log10(value))
    if value > 1:
        expValue = floor(abs(log10(value)))
    else:
        expValue = ceil(abs(log10(value)))
    exponentString = "%+.0f" % int(expSign * expValue)
    
    valueString = ("%0.2e" % value)[:4]
    return str(valueString + "E" + exponentString)
    

class TPG361Controller(object):
    
    

    def __init__(self, serial):
        """
        Creates a new instance of the Pfeiffer TPG361 Single Gauge Controller
        class.
        
        parameters
        ----------
        
        portIODevice: an instance of serial.Serial to communicate with the sensor over RS-232.
        """
        
        self.serial = serial
    
    

    def _query(self,mnemonic,replyConverter=str):
        
        commandString = "%s\r\n".encode() % mnemonic
        self.serial.write(commandString)
        self.serial.flush()
        
        reply = self.serial.readall()
        if reply != '\x06\r\n':
            raise Exception("The device threw an error: %s" % reply)
        else:
            self.serial.write('\x05')
            self.serial.flush()
        reply = self.serial.readall()
                        
        
        try:
            if replyConverter is not None:
                value = replyConverter(reply)
                return value
        except:
            raise Exception("An error occured while parsing the reply: %s" % reply)
       
    
   
    @public
    def getPressure(self):
        """
        Return the current measurement value (PR1)
        """
        
        status, pressure = self._query("PR1",lambda reply: re.findall(r'(\d),\+(\d\.\d\d\d\dE\+\d\d)\r\n',reply)[0])        
        iStatus = int(status)        
        statusDict = {0: 'measurement data ok',
                      1: 'underrange',
                      2: 'overrange',
                      3: 'sensor error',
                      4: 'sensor off',
                      5: 'no sensor',
                      6: 'identification error'}
        
        return dict(pressure = float(pressure), status = statusDict[int(iStatus)], status_int = iStatus)