import time
from binascii import hexlify

def file_comm(cmd_in, cmd_out=None, file_path="Results.txt", start=None, end=None):
    if not cmd_out:
        write_to_file("Device", file_path, cmd_out, start, end)
    else:
        if cmd_in:
            write_to_file("Device", file_path, cmd_in, start, end)
            write_to_file("Computer", file_path, cmd_out, start, end)


def write_to_file(sender, file_path, command, start_body=None, end_body=None):
    hex_cmd = hexlify(command)
    if start_body:

        cmd_head = hex_cmd[:start_body]
        if end_body:
            cmd_body = hex_cmd[start_body:end_body]
            tail = hex_cmd[end_body:]

    with open(file_path, "a") as file:
        if not start_body:
            file.write(f"From:{sender} at {time.ctime()}")
            file.write(f"Command(HEX):{hex_cmd}")
            file.write(f"Command(raw): {command}")
        else:

            file.write(f"From: {sender} at {time.ctime()}")
            file.write(f"Header:{cmd_head}")
            file.write(f"Body: {cmd_body}")
            file.write(f"Tail: {tail}")
            file.write(f"Full command: {command}")
        file.write("")
