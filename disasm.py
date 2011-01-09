#!/usr/bin/python

import mmap
import sys

mnemonic = {
   0x1000 : { "nm" : "rrc",   "op" : "single"},
   0x1040 : { "nm" : "rrc.b", "op" : "single"},
   0x1080 : { "nm" : "swpb",  "op" : "single"},
   0x1100 : { "nm" : "rra",   "op" : "single"},
   0x1140 : { "nm" : "rra.b", "op" : "single"},
   0x1180 : { "nm" : "sxt",   "op" : "single"},
   0x1200 : { "nm" : "push",  "op" : "single"},
   0x1240 : { "nm" : "push.b","op" : "single"},
   0x1280 : { "nm" : "call",  "op" : "single"},
   0x1300 : { "nm" : "reti",  "op" : "single"},
   0x2000 : { "nm" : "jne",   "op" : "jump"  },
   0x2400 : { "nm" : "jeq",   "op" : "jump"  },
   0x2800 : { "nm" : "jnc",   "op" : "jump"  },
   0x2C00 : { "nm" : "jc",    "op" : "jump"  },
   0x3000 : { "nm" : "jn",    "op" : "jump"  },
   0x3400 : { "nm" : "jge",   "op" : "jump"  },
   0x3800 : { "nm" : "jl",    "op" : "jump"  },
   0x3C00 : { "nm" : "jmp",   "op" : "jump"  },
   0x4000 : { "nm" : "mov",   "op" : "double"},
   0x5000 : { "nm" : "add",   "op" : "double"},
   0x6000 : { "nm" :"addc",   "op" : "double"},
   0x7000 : { "nm" :"subc",   "op" : "double"},
   0x8000 : { "nm" :"sub",    "op" : "double"},
   0x9000 : { "nm" :"cmp",    "op" : "double"},
   0xA000 : { "nm" :"dadd",   "op" : "double"},
   0xB000 : { "nm" :"bit",    "op" : "double"},
   0xC000 : { "nm" :"bic",    "op" : "double"},
   0xD000 : { "nm" :"bis",    "op" : "double"},
   0xE000 : { "nm" :"xor",    "op" : "double"},
   0xF000 : { "nm" :"and",    "op" : "double"},
}

def getAddressingMode(asad, word):
    if asad == 'as':
        if word & 0x0030 == 0x0000:
            admode = "RegisterMode"
        elif word & 0x0030 == 0x0010:
            if word & 0x0f00 >= 0x0300 or word & 0x0f00 == 0x0100:
                admode = "IndexedMode"
            elif word & 0x0f00 == 0x0000:
                admode = "SymbolicMode"
            elif word & 0x0f00 == 0x0200:
                admode = "AbsoluteMode"                
        elif word & 0x0030 == 0x0020:
            admode = "IndirectRegisterMode"
        elif word & 0x0030 == 0x0030:
            if word & 0x0f00 >= 0x0100:
                admode = "IndirectAutoIncrement"
            else:
                admode = "ImmediateMode"
        else:
            print 'as err'

    elif asad == 'ad':
        if word & 0x0080 == 0x0000:
            admode = "RegisterMode"
        elif word & 0x0080 == 0x0080:
            if word & 0x000f >= 0x0004:
                admode = "IndexedMode"
            elif word & 0x000f == 0x0000:
                admode = "SymbolicMode"
            elif word & 0x000f == 0x0002:
                admode = "AbsoluteMode"                
        else:
            print 'ad err'
    
    return admode

def getAddModeStr(addMode):
    dicAddMode = {
        "ConstantGenerator" :   ['UNKNOWN_REG'],
        "RegisterMode" :        ['UNKNOWN_REG'],
        "IndexedMode"  :        ['UNKNOWN_VAL', '(', 'UNKNOWN_REG', ')'],
        "SymbolicMode" :        ['UNKNOWN_VAL'],
        "AbsoluteMode" :        ['&', 'UNKNOWN_VAL'],
        "IndirectRegisterMode" :['@', 'UNKNOWN_REG'],
        "IndirectAutoIncrement":['@', 'UNKNOWN_REG', '+'],
        "ImmediateMode":        ['#', 'UNKNOWN_VAL'],
            }

    return dicAddMode[addMode]

def getSrcStr(list, reg = 'UNKNOWN_REG', val = 'UNKNOWN_VAL'):
    src = ''
    for x in list:
        if x == 'UNKNOWN_REG':
            src += reg
        elif x == 'UNKNOWN_VAL':
            src += val
        else:
            src += x
    
    return src

def makeWord(bytes):
    word = ord(bytes[1]) << 8
    word = word + ord(bytes[0])
    return word

def getRegister(register):

    dicReg = {
        0  : 'PC',  1  : 'SP', 2  : 'GC1',
        3  : 'GC2', 4  : 'R4', 5  : 'R5',
        6  : 'R6',  7  : 'R7', 8  : 'R8',
        9  : 'R9',  10 : 'R10',11 : 'R11',
        12 : 'R12', 13 : 'R13',14 : 'R14',
        15 : 'R15',
        }

    return dicReg[register]
        

def disassemble(map):
    bytes = map.read(2)
    while bytes :
        indxval  = ""
        readrawdata = []
        InstructionSet = ""
        WordByte = ""
        Src = ""
        Dest = ""
        PCoffse = ""
        word = makeWord(bytes)
        for x in bytes: readrawdata.append(x)

        if mnemonic.get(word & 0xffc0) != None :
            InstructionSet = mnemonic[word & 0xffc0]["nm"]
            ophash = mnemonic[word & 0xffc0]
        elif mnemonic.get(word & 0xf000) != None :
            InstructionSet = mnemonic[word & 0xf000]["nm"]
            ophash = mnemonic[word & 0xf000]
        else:
            print 'mn err'

        reginame = getRegister((word & 0x0f00) >> 8)
        if reginame == 'GC1':
            if word & 0x0030 == 0x0010:
                reginame = '(0)'
            elif word & 0x0030 == 0x0020:
                reginame = '4'
            elif word & 0x0030 == 0x0030:
                reginame = '8'
        elif reginame == 'GC2':
            if word & 0x0030 == 0x0000:
                reginame = '0'
            elif word & 0x0030 == 0x0010:
                reginame = '1'
            elif word & 0x0030 == 0x0020:
                reginame = '2'
            elif word & 0x0030 == 0x0030:
                reginame = '-1'
            
        if ophash["op"] != "jump" :
            if word & 0x0040 == 0x0040 :
                WordByte = '.b'

        if ophash["op"] == "double" :
            if ( reginame == '(0)'or reginame == '4' or
                 reginame == '8'  or reginame == '0' or
                 reginame == '1'  or reginame == '2' or
                 reginame == '-1'):
                strAddMode = "ConstantGenerator" 
            else:
                strAddMode = getAddressingMode('as',word & 0x0f30)

            srcList = getAddModeStr(strAddMode)

            if strAddMode == "RegisterMode" or strAddMode == "ConstantGenerator":
                Src = getSrcStr(srcList, reginame)

            elif strAddMode == "IndexedMode" or strAddMode == "SymbolicMode":
                bytes = map.read(2)
                indxval = makeWord(bytes)
                for x in bytes: readrawdata.append(x)
                Src = getSrcStr(srcList, reginame, hex(indxval))

            elif strAddMode == "AbsoluteMode":
                bytes = map.read(2)
                indxval = makeWord(bytes)
                for x in bytes: readrawdata.append(x)
                Src = getSrcStr(srcList, 'UNKNOWN_REG', hex(indxval))

            elif strAddMode == "IndirectRegisterMode":
                Src = getSrcStr(srcList, reginame)

            elif strAddMode == "IndirectAutoIncrement":
                Src = getSrcStr(srcList, reginame)

            elif strAddMode == "ImmediateMode":
                bytes = map.read(2)
                indxval = makeWord(bytes)
                for x in bytes: readrawdata.append(x)
                Src = getSrcStr(srcList, 'UNKNOWN_REG', hex(indxval))

            strAddMode = getAddressingMode('ad',word & 0x008f)
            destList = getAddModeStr(strAddMode)
            destRegname = getRegister(word & 0x000f)
            
            if strAddMode == "RegisterMode":
                Dest = getSrcStr(destList, destRegname)

            elif strAddMode == "IndexedMode" or strAddMode == "SymbolicMode":
                bytes = map.read(2)
                indxval = makeWord(bytes)
                for x in bytes: readrawdata.append(x)
                Dest = getSrcStr(destList, destRegname, hex(indxval))

            elif strAddMode == "AbsoluteMode":
                bytes = map.read(2)
                indxval = makeWord(bytes)
                for x in bytes: readrawdata.append(x)
                Dest = getSrcStr(destList, 'UNKNOWN_REG', hex(indxval))

        elif ophash["op"] == "single" :
            strAddMode = getAddressingMode('ad',word & 0x008f)
            destList = getAddModeStr(strAddMode)
            destRegname = getRegister(word & 0x000f)

            if strAddMode == "RegisterMode":
                if InstructionSet != 'reti':
                    Dest = getSrcStr(destList, destRegname)

            elif strAddMode == "IndexedMode" or strAddMode == "SymbolicMode":
                bytes = map.read(2)
                indxval = makeWord(bytes)
                for x in bytes: readrawdata.append(x)
                Dest = getSrcStr(destList, destRegname, hex(indxval))

            elif strAddMode == "AbsoluteMode":
                bytes = map.read(2)
                indxval = makeWord(bytes)
                for x in bytes: readrawdata.append(x)
                Dest = getSrcStr(destList, 'UNKNOWN_REG', hex(indxval))

        elif ophash["op"] == "jump" :
            PCoffset =  hex((word & 0x00ff) * 2)

        strrawdata = ""
        for x in readrawdata:
            strrawdata += format(ord(x),'02x') + ' '

        print '%-20s' % strrawdata,

        if ophash["op"] == "jump" :
            print InstructionSet + ' ' + PCoffset
        elif InstructionSet == "reti" :
            print InstructionSet
        else:
            print InstructionSet + WordByte + ' ' + Src + ',' + Dest

        bytes = map.read(2)


if len(sys.argv) != 2:
    sys.exit()

with open(sys.argv[1], "r+b") as f:
    map = mmap.mmap(f.fileno(), 0)
    disassemble(map)
    map.close()
