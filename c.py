import math

class Memory(object):
    """
    This class controls the virtual memory space of the simulator.
    """
    def init_mem(self):
        """
        This method resets the Cardiac's memory space to all blank strings, as per Cardiac specs.
        """
        self.mem = ['' for i in range(0,100)]
        self.mem[0] = '001' #: The Cardiac bootstrap operation.

    def get_memint(self, data):
        """
        Since our memory storage is *string* based, like the real Cardiac, we need
        a reusable function to grab a integer from memory.  This method could be
        overridden if say a new memory type was implemented, say an mmap one.
        """
        return int(self.mem[data])

    def pad(self, data, length=3):
        """
        This function pads either an integer or a number in string format with
        zeros.  This is needed to replicate the exact behavior of the Cardiac.
        """
        orig = int(data)
        padding = '0'*length
        data = '%s%s' % (padding, abs(data))
        if orig < 0:
            return '-'+data[-length:]
        return data[-length:]


class IO(object):
    """
    This class controls the virtual I/O of the simulator.
    To enable alternate methods of input and output, swap this.
    """
    def init_reader(self):
        """
        This method initializes the input reader.
        """
        self.reader = [] #: This variable can be accessed after initializing the class to provide input data.

    def init_output(self):
        """
        This method initializes the output deck/paper/printer/teletype/etc...
        """
        self.output = []

    def read_deck(self, fname):
        """
        This method will read a list of instructions into the reader.
        """
        self.reader = [s.rstrip('\n') for s in open(fname, 'r').readlines()]
        self.reader.reverse()

    def format_output(self):
        """
        This method is to format the output of this virtual IO device.
        """
        return '\n'.join(self.output)

    def get_input(self):
        """
        This method is used to get input from this IO device, this could say
        be replaced with raw_input() to manually enter in data.
        """
        try:
            return self.reader.pop()
        except IndexError:
            # Fall back to raw_input() in the case of EOF on the reader.
            return raw_input('INP: ')[:3]

    def stdout(self, data):
        self.output.append(data)


class CPU(object):
    """
    This class is the cardiac "CPU".
    """
    def __init__(self):
        self.init_cpu()
        self.reset()
        try:
            self.init_mem()
        except AttributeError:
            raise NotImplementedError('You need to Mixin a memory-enabled class.')
        try:
            self.init_reader()
            self.init_output()
        except AttributeError:
            raise NotImplementedError('You need to Mixin a IO-enabled class.')

    def reset(self):
        """
        This method resets the CPU's registers to their defaults.
        """
        self.pc = 0 #: Program Counter
        self.ir = 0 #: Instruction Register
        self.acc = 0 #: Accumulator
        self.running = False #: Are we running?

    def init_cpu(self):
        """
        This fancy method will automatically build a list of our opcodes into a hash.
        This enables us to build a typical case/select system in Python and also keeps
        things more DRY.  We could have also used the getattr during the process()
        method before, and wrapped it around a try/except block, but that looks
        a bit messy.  This keeps things clean and simple with a nice one-to-one
        call-map. 
        """
        self.__opcodes = {}
        classes = [self.__class__] #: This holds all the classes and base classes.
        while classes:
            cls = classes.pop() # Pop the classes stack and being
            if cls.__bases__: # Does this class have any base classes?
                classes = classes + list(cls.__bases__)
            for name in dir(cls): # Lets iterate through the names.
                if name[:7] == 'opcode_': # We only want opcodes here.
                    try:
                        opcode = int(name[7:])
                    except ValueError:
                        raise NameError('Opcodes must be numeric, invalid opcode: %s' % name[7:])
                    self.__opcodes.update({opcode: getattr(self, 'opcode_%s' % opcode)})

    def fetch(self):
        """
        This method retrieves an instruction from memory address pointed to by the program pointer.
        Then we increment the program pointer.
        """
        self.ir = self.get_memint(self.pc)
        self.pc += 1

    def process(self):
        """
        Process a single opcode from the current program counter.  This is
        normally called from the running loop, but can also be called
        manually to provide a "step-by-step" debugging interface, or
        to slow down execution using time.sleep().  This is the method
        that will also need to used if you build a TK/GTK/Qt/curses frontend
        to control execution in another thread of operation.
        """
        self.fetch()
        opcode, data = int(math.floor(self.ir / 100)), self.ir % 100
        self.__opcodes[opcode](data)

    def opcode_0(self, data):
        """ INPUT Operation """
        self.mem[data] = self.get_input()

    def opcode_1(self, data):
        """ Clear and Add Operation """
        self.acc = self.get_memint(data)

    def opcode_2(self, data):
        """ Add Operation """
        self.acc += self.get_memint(data)

    def opcode_3(self, data):
        """ Test Accumulator contents Operation """
        if self.acc < 0:
            self.pc = data

    def opcode_4(self, data):
        """ Shift operation """
        x,y = int(math.floor(data / 10)), int(data % 10)
        for i in range(0,x):
            self.acc = (self.acc * 10) % 10000
        for i in range(0,y):
            self.acc = int(math.floor(self.acc / 10))

    def opcode_5(self, data):
        """ Output operation """
        self.stdout(self.mem[data])

    def opcode_6(self, data):
        """ Store operation """
        self.mem[data] = self.pad(self.acc)

    def opcode_7(self, data):
        """ Subtract Operation """
        self.acc -= self.get_memint(data)

    def opcode_8(self, data):
        """ Unconditional Jump operation """
        self.pc = data

    def opcode_9(self, data):
        """ Halt and Reset operation """
        self.reset()

    def run(self, pc=None):
        """ Runs code in memory until halt/reset opcode. """
        if pc:
            self.pc = pc
        self.running = True
        while self.running:
            self.process()
        print "Output:\n%s" % self.format_output()
        self.init_output()

class Cardiac(CPU, Memory, IO):
    pass

if __name__ == '__main__':
    c = Cardiac()
    c.read_deck('test')
    try:
        c.run()
    except:
        print "IR: %s\nPC: %s\nOutput: %s\n" % (c.ir, c.pc, c.format_output())
        raise
