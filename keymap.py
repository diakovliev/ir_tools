import os
import json

class Keymap:

    class __Entry(dict):
        def __init__(self, protocol, bits, address, value):
            dict.__init__(self)
            self['protocol'] = protocol
            self['bits']     = bits
            self['address']  = address
            self['value']    = value

        def __eq__(self, other):
            return self['protocol'] == other['protocol'] and self['bits'] == other['bits'] and self['address'] == other['address'] and self['value'] == other['value']

    def __init__(self, filename):
        self.__filename = filename
        if os.path.isfile(self.__filename):
            with open(self.__filename, 'r') as f:
                self.__map = json.load(f)
        else:
            self.__map = {}

    def translate(self, protocol, bits, address, value):
        entry_to_translate = self.__Entry(protocol, bits, address, value)
        for key, value in self.__map.items():
            if value == entry_to_translate:
                return key

        return None

    def find(self, name):
        for key, value in self.__map.items():
            if key == name:
                return value

        return None

    def __write(self):
        with open(self.__filename, 'w') as f:
            json.dump(self.__map, f)

    def register(self, name, protocol, bits, address, value):
        assert name not in self.__map
        self.__map[name] = self.__Entry(protocol, bits, address, value)
        self.__write()

    def update(self, name, protocol, bits, address, value):
        assert name in self.__map
        self.__map[name] = self.__Entry(protocol, bits, address, value)
        self.__write()

    @staticmethod
    def format(entry):
        return "%dp%da%db%dv" % (entry['protocol'], entry['address'], entry['bits'], entry['value'])

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
