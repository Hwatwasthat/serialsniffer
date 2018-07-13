from src.single import SinglePort
from time import sleep

class PairOfPorts:
    ERR_STR = "Pair.PairofPorts."
    def __init__(self, ser_in, ser_out, cmd_in, cmd_out, timeout=0):
        """
        Initiates a Pair of ports class, handles both incoming and outgoing ports.
        :param ser_in: Serial port to be used for incoming messages from
                       external devices.
        :param ser_out: Serial port to be used to connect to virtual port.
        :param cmd_in: size of expected command in from device.
        :param cmd_out: size of expected command out from computer.
        :param timeout: inter-byte-timeout period.
        """
        self.ser_in = SinglePort(ser_in, cmd_in, timeout)
        self.ser_out = SinglePort(ser_out, cmd_out, timeout)

    def open_ports(self):
        return (self.ser_in.open_port(self.ERR_STR + "open_ports"),
                self.ser_out.open_port(self.ERR_STR + "open_ports"))

    def close_port(self):
        return (self.ser_in.close_port(self.ERR_STR + "close_ports"),
                self.ser_out.close_port(self.ERR_STR + "close_ports"))

    def communication(self):
        """
        Checks ports for waiting bytes. If computer has message to send, sends
        to device and allows processing time then checks for response.
        :return: returns commands that were exchanged.
        """
        in_cmd, out_cmd = "", ""

        out_cmd = self.ser_out.read_command()
        if out_cmd:
            self.ser_in.send_command(out_cmd)
            sleep(0.5)  # Allow time for device to compute response


        in_cmd = self.ser_in.read_command()
        if in_cmd:
            self.ser_out.send_command(in_cmd)

        return in_cmd, out_cmd

