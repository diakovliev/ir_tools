import os
import json
import argparse
import serial

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

    args    = parser.parse_args()
    keymap  = Keymap(args.keymap)
    ser     = serial.Serial(args.device, Commons.SERIAL_SPEED, parity=serial.PARITY_NONE)

    while True:
        l = ser.readline().decode(Commons.ENCODING).strip()
        if l.startswith(" -- "):
            print("%s" % l)
        else:
            params = l.split(',')
            print(repr(params))

            assert params[0] == "r"
            protocol = int(params[1])
            bits     = int(params[2])
            address  = int(params[3])
            value    = int(params[4])

            keyname = keymap.translate(protocol, bits, address, value)
            if keyname is not None:
                print(" -- key '%s' { protocol: %d, bits: %d, address: %d, value: %d }" % (keyname, protocol, bits, address, value))
                continue

            print(" -- unknown key { protocol: %d, bits: %d, address: %d, value: %d }" % (protocol, bits, address, value))
            keyname = input("Enter key name: ")

            keymap.register(keyname, protocol, bits, address, value)



if __name__ == "__main__":
    main()
