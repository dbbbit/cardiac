class Assembler(object):
    """
    op_code for cardiac: OPERATOR + memory address[00-99];
    bootstrap op_code: 001 in cell 00;

    ["001", "xxx" "800"] read sth to cell 01 then execute it, jmp back to 00 again;
    """
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
        self.data_p = 3
        self.code_p = 10
        self.labels = {}  # label_name: label_line

    def read_source(self, filename):
        """
        This method will read a list of instructions into the reader.
        """
        self.reader = [s.rstrip('\n') for s in open(filename, 'r').readlines()]
        self.reader.reverse()

    def prepare(self):
        source_code = self.reader[:]
        code_p = self.code_p
        data_p = self.data_p
        while len(source_code):
            line = source_code.pop()
            toks = [tok.lower() for tok in line.split()]
            if not toks:
                continue
            if toks[0] not in self.OPERATORS and len(toks) >= 3:
                label_name = toks[0]
                if toks[1] == 'data':
                    self.labels[label_name] = data_p
                else:
                    self.labels[label_name] = code_p
                toks.remove(toks[0])
            if toks[0] in self.OPERATORS and len(toks) >= 2:
                code_p += 1
            if toks[0] == 'data' and len(toks) >= 2:
                data_p += 1

    def compile(self):
        self.prepare()
        while len(self.reader):
            line = self.reader.pop()
            toks = [tok.lower() for tok in line.split()]
            if not toks:
                continue
            if toks[0] not in self.OPERATORS and len(toks) >= 3:
                toks.remove(toks[0])
            if len(toks) >= 2 and toks[0] == 'data':
                self.output.append(self.pad(self.data_p))
                self.output.append(toks[1])
                self.data_p += 1
                continue
            if len(toks) >= 2 and toks[0] in self.OPERATORS:
                operation = toks[0]
                address = toks[1]
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
