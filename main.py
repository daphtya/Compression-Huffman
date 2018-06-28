import sys
import os
import compressed as cmp

def doCompress(namaFile):
    comp = cmp.Compress(namaFile)
    comp.compress()
    namatemp = namaFile.split('.')
    namatemp[-1] = 'irk'
    namabaru = '.'.join(namatemp)
    with open(namabaru, 'wb') as newfile:
        newfile.write(comp.toBytes())
    return comp

def decompress(namaFile):
    with open(namaFile, 'rb') as file:
        extension = ""
        byte = file.read(1)
        while byte != b'.':
            extension += byte.decode('ascii')
            byte = file.read(1)
        namabaru = namaFile.split('.')
        namabaru[-1] = extension
        namabaru = '.'.join(namabaru)
        
        padding = ord(file.read(1))
        print(padding)
        algo = cmp.HuffmanAlgorithm()
        algo.decodeTree(file)
        codes = algo.assignCodes(reversed=True)
        with cmp.BitReader(file) as reader:
            with open(namabaru, 'wb') as decoded:
                filesize = os.fstat(file.fileno()).st_size
                while file.tell() < filesize or reader.bcount > padding:
                    code = ""
                    while code not in codes:
                        code += str(reader.readbits(1))
                    decoded.write(codes[code])
                print(codes, code)
                print(reader.bcount)
                
                

if len(sys.argv) > 1:
    if sys.argv[2] == '1':
        doCompress(sys.argv[1])
    elif sys.argv[2] == '2':
        decompress(sys.argv[1])
