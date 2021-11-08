import sys
import serial
import argparse

from keymap import Keymap
from commons import Commons

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--device",
        action="store",
        help="Serial device.",
        required=True,
    )
    parser.add_argument("--keymap",
        action="store",
        help="Keymap file.",
        required=True,
    )
    parser.add_argument("--send",
        action="store",
        help="Key to send.",
        required=True,
    )

    args    = parser.parse_args()
    keymap  = Keymap(args.keymap)
    ser     = serial.Serial(args.device, Commons.SERIAL_SPEED, parity=serial.PARITY_NONE)

    cmd     = keymap.find(args.send)
    if cmd is None:
        print("Unknown key '%s'" % args.send)
        sys.exit(-1)

    command_to_send = "%s\n" % Keymap.format(cmd)

    while True:
        l = ser.readline().decode(Commons.ENCODING)
        if not l.strip():
            continue

        print(">> %s" % l)
        if l.startswith(" -- "):
            continue

        if l.strip() == "READY":
            ser.write(command_to_send.encode(Commons.ENCODING))
            continue

        params = l.strip().split(',')
        print(repr(params))

        assert params[0] == "t"
        protocol = int(params[1])
        bits     = int(params[2])
        address  = int(params[3])
        value    = int(params[4])

        if cmd['protocol'] == protocol and cmd['bits'] == bits and cmd['address'] == address and cmd['value'] == value:
            break

if __name__ == "__main__":
    main()
