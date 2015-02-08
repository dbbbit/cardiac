class Assembler(object):
    OPERATORS = {
        "inp": 0,
        "cla": 1,
        "add": 2,
        "tac": 3,
        "sft": 4,
        "out": 5,
        "sto": 6,
        "sub": 7,
        "jmp": 8,
        "hrs": 9,
    }

    def __init__(self):
        self.reader = []
        self.output = ["002", "800"]
        self.data_p = 4
        self.code_p = 10
        self.labels = {}  # key:value => label:addr

    def read_source(self, filename):
        """
        This method will read a list of instructions into the reader.
        """
        self.reader = [s.rstrip('\n') for s in open(filename, 'r').readlines()]
        self.reader.reverse()

    def pre(self):
        #: get all labels
        source = self.reader[:]
        code_p = self.code_p
        data_p = self.data_p
        while len(source):
            text = source.pop()
            tks = [tk.lower() for tk in text.split()]

            #: pass space or tab
            if not tks:
                continue

            #: label
            if tks[0] not in self.OPERATORS and len(tks) >= 3:
                label_name = tks[0]
                if tks[1] == 'data':
                    self.labels[label_name] = data_p
                else:
                    self.labels[label_name] = code_p
                tks.remove(tks[0])

            if len(tks) >= 2 and tks[0] in self.OPERATORS:
                code_p += 1

            if len(tks) >= 2 and tks[0] == 'data':
                data_p += 1

    def compile(self):
        self.pre()
        while len(self.reader):
            text = self.reader.pop()
            tks = [tk.lower() for tk in text.split()]

            #: pass space or tab
            if not tks:
                continue

            #: label
            if tks[0] not in self.OPERATORS and len(tks) >= 3:
                tks.remove(tks[0])

            #: data
            if len(tks) >= 2 and tks[0] == 'data':
                self.output.append(self.pad(self.data_p))
                self.output.append(tks[1])
                self.data_p += 1
                continue

            #: instruction
            if len(tks) >= 2 and tks[0] in self.OPERATORS:
                operation = tks[0]
                address = tks[1]
                op = str(self.OPERATORS[operation])
                if address in self.labels:
                    address = self.pad(self.labels[address], length=2)
                code = op + address
                self.output.append(self.pad(self.code_p))
                self.output.append(code)
                self.code_p += 1
                continue

            print "error instruction: %s\n" % tks
            break
        self.output.append("002")
        self.output.append("810")

    @staticmethod
    def pad(data, length=3):
        """
        This function pads either an integer or a number in string format with zeros.
        This is needed to replicate the exact behavior of the Cardiac.
        """
        orig = int(data)
        padding = '0' * length
        data = '%s%s' % (padding, abs(data))
        if orig < 0:
            return '-' + data[-length:]
        return data[-length:]

    def format_output(self):
        for code in self.output:
            print code


def main():
    a = Assembler()
    a.read_source('./test.src')
    a.compile()
    a.format_output()


if __name__ == "__main__":
    main()
