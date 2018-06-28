import sys
import queue

class BitWriter(object):
    def __init__(self, f=None):
        self.accumulator = 0
        self.bcount = 0
        self.out = f
        self.array = bytearray()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        #self.flush()
        pass

    def __del__(self):
        try:
            #self.flush()
            pass
        except ValueError:   # I/O operation on closed file.
            pass

    def _writebit(self, bit):
        if self.bcount == 8:
            self.flush()
        if bit > 0:
            self.accumulator |= 1 << 7-self.bcount
        self.bcount += 1

    def writebits(self, bits, n):
        while n > 0:
            self._writebit(bits & 1 << n-1)
            n -= 1

    def flush(self):
        if self.out != None:
            self.out.write(bytearray([self.accumulator]))
        else:
            self.array.append(self.accumulator)
        self.accumulator = 0
        self.bcount = 0


class BitReader(object):
    def __init__(self, f):
        self.input = f
        self.accumulator = 0
        self.bcount = 0
        self.read = 0
        self.end = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def _readbit(self):
        if self.bcount == 0:
            if not isinstance(self.input, bytearray):
                a = self.input.read(1)
                if a != b'':
                    self.accumulator = ord(a)
                else:
                    self.end = True
            else:
                if self.read < len(self.input):
                    self.accumulator = self.input[self.read]
                else:
                    self.end = True
            self.bcount = 8
            self.read += 1
            
        rv = (self.accumulator & (1 << self.bcount-1)) >> self.bcount-1
        self.bcount -= 1
        return rv

    def readbits(self, n):
        v = 0
        while n > 0:
            v = (v << 1) | self._readbit()
            n -= 1
        return v


class HuffmanTree:
    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right

    def _assigncode(self, prefix="", table={}):
        if isinstance(self.left, HuffmanTree):
            self.left._assigncode(prefix + '0', table)
        else:
            table[self.left] = prefix + '0'
        if isinstance(self.right, HuffmanTree):
            self.right._assigncode(prefix + '1', table)
        else:
            table[self.right] = prefix + '1'

    def getCodes(self):
        codes = {}
        self._assigncode(table = codes)
        return codes


class DataWrapper:
    """wrapper untuk menghindari bug di prioqueue saat priority number tidak unik"""
    def __init__(self, data):
        self.data = data
    
    def __lt__(self, other):
        return True


class HuffmanAlgorithm:
    def __init__(self):
        self.codes = {}
        self.tree = HuffmanTree()


    def buildTree(self, frequency):
        """ build a huffman tree based on frequency """
        freq = [(x[1], DataWrapper(x[0])) for x in frequency.items()]
        pq = queue.PriorityQueue()
        for item in freq:
            pq.put(item)
        while pq.qsize() > 1:
            left, right = pq.get(), pq.get()
            pq.put((left[0]+right[0], DataWrapper(HuffmanTree(left[1].data, right[1].data))))
        completeTree = pq.get()
        self.tree = completeTree[1].data
        
    def assignCodes(self, reversed=False):
        """ return a dictionary of codes for each item 
            based on huffman tree """    
        self.codes = self.tree.getCodes()
        if reversed:
            revcode = {}
            for key in self.codes:
                revcode[self.codes[key]] = key
            self.codes = revcode
        return self.codes

    def encodeTree(self):
        """ encode the huffman tree into a string of bytes """
        with BitWriter() as writer:
            self._encodeTreeNodes(self.tree, writer)
            if writer.bcount > 0:
                writer.flush()
            arraytree = writer.array
        return arraytree

    def _encodeTreeNodes(self, tree, writer):
        writer.writebits(0,1)
        if isinstance(tree.left, HuffmanTree):
            self._encodeTreeNodes(tree.left, writer)
        else:
            writer.writebits(1, 1)
            writer.writebits(ord(tree.left), 8)

        if isinstance(tree.right, HuffmanTree):
            self._encodeTreeNodes(tree.right, writer)
        else:
            writer.writebits(1,1)
            writer.writebits(ord(tree.right), 8)
        
    def decodeTree(self, file):
        """ create a tree by reading the file until the tree is complete """
        with BitReader(file) as reader:
            self.tree = self._decode(reader)

    def _decode(self, reader):    
        isTree = reader.readbits(1)
        #print('istree: ',isTree) #debug
        if isTree == 0:
            output = HuffmanTree()
            output.left = self._decode(reader)
            output.right = self._decode(reader)
        else:
            output = reader.readbits(8).to_bytes(1,'big')
        return output

class Compress:
    def __init__(self, file):
        self.file = file
        self.bitsout = bytearray()

    def _sortbytes(self):
        """ returns a dictionary of occurences for each byte """
        table = {}
        with open(self.file, "rb") as file:
            byte = file.read(1)
            while byte != b'':
                if byte not in table:
                    table[byte] = 1
                else:
                    table[byte] += 1
                byte = file.read(1)
        return table

    def _stringToBits(self, binaryString):
        bits = 0
        for i in range(len(binaryString)):
            bits = bits * 2 + int(binaryString[i])
        return bits

    def compress(self):
        freq = self._sortbytes()
        algo = HuffmanAlgorithm()
        algo.buildTree(freq)
        codes = algo.assignCodes()

        extension = self.file.split('.')[-1]
        header = bytearray(extension + '.', 'ascii')

        tree = algo.encodeTree()
        
        with open(self.file, 'rb') as file:
            with BitWriter() as writer:
                byte = file.read(1)
                while byte != b"":
                    temp = codes[byte]
                    writer.writebits(self._stringToBits(temp), len(temp))
                    byte = file.read(1)
                padding = 0
                if writer.bcount > 0:
                    padding = 8 - writer.bcount
                    writer.flush()
                encodedfile = writer.array

        self.bitsout = header + bytearray([padding]) + tree + encodedfile
        #karena tree + file, gunakan BitReader berbeda untuk membaca tree dan file saat decompress!

    def toBytes(self):
        return self.bitsout

    