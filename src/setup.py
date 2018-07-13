from src import pair, single
from serial import Serial, SerialException


def setup(port1, port1_cmd=10000, port2=None, port2_cmd=None, timeout=0):
    if not port2:
        return single.SinglePort(port1, port1_cmd, timeout)
    else:
        return pair.PairOfPorts(port1, port2, port1_cmd, port2_cmd, timeout)

def find_ports():
    list_ports = []
    for i in range(256):
        try:
            s = Serial('COM{}'.format(str(i)))
            list_ports.append(s.port)
            s.close()
        except SerialException:
            pass

    return list_ports

def full_setup(ser):
    ser1, ser2 = ser
    ser = setup(port1=ser1, port2=ser2)
    if type(ser) == single.SinglePort:
        loop = False
    else:
        loop = True

    return ser, loop