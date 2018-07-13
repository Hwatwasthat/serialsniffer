from src import single, setup, file_data
from serial import Serial, SerialException
from msvcrt import kbhit, getwch
from sys import exit


def setup_connections():
    list_ports = setup.find_ports()
    print("Ports available:")
    print(" ".join(list_ports))
    ser_num = 'COM{}'.format(input("\nPlease enter number of COM port to use for device:"))
    print('\n')
    ser_out = "COM{}".format(input("\nIf two way communications, enter port for pass through, else enter N:"))
    print('\n')
    cmd_size = input("If there are any cmd size limits, please enter, else enter N:")
    if cmd_size == "N":
        cmd_size = 10000
    if ser_out == "COMN":
        return ser_num
    else:
        return ser_num, ser_out

def end_loop(overall_count, ser):
    """
    Safely closes connection and outputs the final results of commands received.
    :param overall_count: Amount of messages exchanged, counts both in and out.
    :param ser: Serial object containing device information.
    :return:
    """
    ser.close_port("end_loop")

    print(f'\n{str(overall_count)} Commands received')

    with open('results.txt', 'a') as out_file:
        out_file.write(
            f'\nSerial monitoring ended. {str(overall_count)} commands received from device.')
    exit(0)


def main():
    """
    Main function, starts all other functions, contains primary while loop.
    :return: No return value.
    """
    count = 0
    print('\n-------------------------------------------------------\n'
          'Welcome to serial monitor. Press e at any time to exit.'
          '\n-------------------------------------------------------\n')
    ser, loop = setup.full_setup(setup_connections())

    # Loop until interrupted by a button press of e
    while True:
        if loop:
            cmd_in, cmd_out = ser.communication()
            file_data.file_comm(cmd_in, cmd_out)
            if cmd_in:
                count += 1
                print("Command received from device:")
                print(cmd_in)
            if cmd_out:
                count += 1
                print("Command received from computer:")
                print(cmd_out)
        else:
            cmd_in = ser.read_command()
            file_data.file_comm(cmd_in)
            if cmd_in:
                count += 1
                print("Command received from device:")
                print(cmd_in)

        if kbhit() and getwch() == 'e':  # Used for apparently async exit
            end_loop(count, ser)

if __name__ == '__main__':
    main()