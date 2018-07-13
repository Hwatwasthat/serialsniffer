from time import sleep
from serial import Serial, SerialException


class SinglePort:

    def __init__(self, serial_port, cmd_size, timeout=0):
        """
        Initiates a single COM port monitor.
        :param serial_port: The COM port to be monitored.
        :param cmd_size: The expected size of a command to be received.
        :param timeout:  The timeout value for gaps between bytes.
        """
        self.serial_port = serial_port
        self.cmd_size = cmd_size
        self.timeout = timeout
        self.ser = Serial()

    def open_port(self, caller):
        """
        Attempts to open the serial port.
        :return: returns whether successful or not.
        """
        try:
            self.ser = Serial(self.serial_port, inter_byte_timeout=self.timeout)
            return f"Port:{self.serial_port} opened"

        except Exception as e:
            print(f"Port:{self.serial_port} failed to open due to: {e}\n"
                  f"Called by: {caller}")

    def close_port(self, caller):
        """
`       Attempts to close the serial port.
        :return: returns whether successful or not.
        """
        try:
            self.ser.close()
            return f"Port:{self.serial_port} closed"

        except Exception as e:
            print(f"Port:{self.serial_port} failed to close due to: {e}\n"
                  f"Called by: {caller}")

    def send_command(self, command):
        """
        sends a command to the port.
        :param command: command to be sent.
        :return: No return.
        """
        self.ser.write(command)

    def read_command(self):
        """
        checks if data is waiting on the port. If it is, data is read and then
        a small delay is taken to ensure all data is received prior to returning.
        :return: command received.
        """
        command  = ""
        if self.check_port():
            command = self.ser.read(self.cmd_size)
            sleep(0.2)  # Required rest space, as devices aren't always 100% consistent
                        # in transfer rate.

            if self.check_port():  # See if anything is waiting to be read after sleep
                command += self.ser.read(self.ser.in_waiting)

        return command

    def check_port(self):
        """
        checks if data is waiting in the port buffer.
        :return: True or False depending on whether buffer contains data.
        """
        if self.ser.in_waiting:
            return True
        else:
            return False
