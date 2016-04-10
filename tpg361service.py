import serial
from tpg361 import TPG361Controller
import argparse
import zmq

from tinyrpc.transports.zmq import ZmqServerTransport
from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc.dispatch import RPCDispatcher

from tinyrpc.server import RPCServer

from os import system


def portNameToInt(portName):
    if (portName.startswith("COM") and len(portName) > 3):
        return int(portName[3:])-1


if __name__=="__main__":
    
    system("Title "+"Device Service: feiffer TPG361 Pressure Sensor")    

    parser = argparse.ArgumentParser(description="Device service for a Pfeiffer TPG361 Pressure Sensor")
    parser.add_argument("--device-port","-d",dest="serialPortName",type=str,default="COM8")
    parser.add_argument("--baud-rate","-b",dest="baudrate",type=int,default=9600)
    parser.add_argument("--service-port","-p",dest="servicePort",type=int,default=5005)
    parser.add_argument("--service-ip",dest="serviceIP",type=str,default="127.0.0.1")
    
    args = parser.parse_args()
    
    serial = serial.Serial(port=portNameToInt(args.serialPortName),
                           baudrate=args.baudrate,
                           parity=serial.PARITY_NONE,
                           timeout=0.1)
    
    tpg = TPG361Controller(serial)
    
                           
    dispatcher = RPCDispatcher()
    dispatcher.register_instance(tpg)
    

    ctx = zmq.Context()
    
    endpoint = 'tcp://%s:%i' % (args.serviceIP,args.servicePort)
    transport = ZmqServerTransport.create(ctx, endpoint)
    print "serving requests at %s" % endpoint
    
    
    rpc_server = RPCServer(
        transport,
        JSONRPCProtocol(),
        dispatcher
    )
    
    rpc_server.serve_forever()