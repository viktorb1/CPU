"""
Copyright (c) 2018, Christopher Nitta
All rights reserved.

This assembler has been provided to the students of ECS 154A at the University
of California, Davis. It is for class use only and not to be redistributed 
without the written consent of the copyright owner.
"""
import glob
import os
import sys
import csv
import chardet

def DetectFileEncoding(filename):
    with open(filename, 'rb') as InFile:
        Detection = chardet.detect(InFile.read())
        return Detection['encoding']

def IsInt(string):
    try:
        if len(string):
            if string[0].lower() == 'b':
                int(string[1:],2)
                return True
            elif string[0].lower() == 'x':
                int(string[1:],16)
                return True
        int(string)
        return True
    except ValueError:
        return False

def ToInt(string):
    if len(string):
        if string[0].lower() == 'b':
            return int(string[1:],2)
        elif string[0].lower() == 'x':
            return int(string[1:],16)
    return int(string)

def RegOrDataToInt(string):
    return ToInt(string[1:])

class Assembler:
    REGISTER_COUNT = 8
    
    LINE_TYPE_EMPTY = 0
    LINE_TYPE_LABEL = 1
    LINE_TYPE_INSTRUCTION = 2
    LINE_TYPE_DATA = 3
    LINE_TYPE_INVALID = 4
        
    TOKEN_TYPE_IDENTIFIER = 0
    TOKEN_TYPE_REGISTER = 1
    TOKEN_TYPE_CONSTANT = 2
    TOKEN_TYPE_COMMA = 3
    TOKEN_TYPE_COLON = 4
    TOKEN_TYPE_PLUS = 5
    TOKEN_TYPE_MINUS = 6
    TOKEN_TYPE_FLAG = 7
    TOKEN_TYPE_INVALID = 8
    
    MAX_POSITIVE_DATA_VALUE = 32767
    MAX_NEGATIVE_DATA_VALUE = -16384
    
    MAX_POSITIVE_BRANCH_OFFSET = 63
    MAX_NEGATIVE_BRANCH_OFFSET = -64
    
    def __init__(self,transfile):
        with open(transfile, 'r', encoding=DetectFileEncoding(transfile)) as TranslationFile:
            TranslationCSVReader = csv.reader(TranslationFile, delimiter=',')
            self.TranslationLoaded = False
            HeaderLine = next(TranslationCSVReader)
            ColumnTranslation = dict()
            self.FlagIndices = dict()
            IndexToFlag = dict()
            for ColumnIndex,ColumnHeader in enumerate(HeaderLine):
                ColumnTranslation[ColumnHeader] = ColumnIndex
                
            for Row in TranslationCSVReader:
                if 'Instruction' in Row:
                    HeaderLine = Row
                    break
                FlagName = Row[ColumnTranslation['Flag']]
                IndexValue = Row[ColumnTranslation['Index']]
                if not IsInt(IndexValue):
                    print('Invalid flag index for {}'.format(FlagName))
                    return
                IndexValue = int(IndexValue)
                if FlagName in self.FlagIndices:
                    print('Duplicate flag listing {}'.format(FlagName))
                if IndexValue in IndexToFlag:
                    print('Duplicate flag index {}'.format(IndexValue))
                self.FlagIndices[FlagName] = IndexValue
                IndexToFlag[IndexValue] = FlagName
                
            ColumnTranslation = dict()
            for ColumnIndex,ColumnHeader in enumerate(HeaderLine):
                ColumnTranslation[ColumnHeader] = ColumnIndex
            self.InstructionToMachine = {'LIL':-1}
            
            MachineToInstruction = dict()
            for Row in TranslationCSVReader:
                IBits = [Row[ColumnTranslation['I4']], Row[ColumnTranslation['I3']], Row[ColumnTranslation['I2']], Row[ColumnTranslation['I1']], Row[ColumnTranslation['I0']] ]
                MachineCode = 0
                for IBit in IBits:
                    MachineCode *= 2
                    MachineCode += 0 if IBit == '0' else 1
                InstructionName = Row[ColumnTranslation['Instruction']]
                if MachineCode in MachineToInstruction:
                    print('Duplicate machine code {:05b}'.format(MachineCode))
                    return
                if InstructionName in self.InstructionToMachine:
                    print('Duplicate instruction name {}'.format(InstructionName))
                    return
                MachineToInstruction[MachineCode] = InstructionName
                self.InstructionToMachine[InstructionName] = MachineCode
            self.TranslationLoaded = True
            
    def ParseLine(self, line, linenumber):
        CommentRemovedLine = line.split(';')[0]
        StrippedLine = CommentRemovedLine.strip()
        if len(StrippedLine):
            TempTokens = StrippedLine.upper().split()
            LineTokens = list()
            for Token in TempTokens:
                TempSplitTokens = Token.split(',')
                CommaSplitTokens = list()
                for SplitIndex, TempSplitToken in enumerate(TempSplitTokens):
                    if SplitIndex:
                        CommaSplitTokens.append(',')
                    if len(TempSplitToken):
                        CommaSplitTokens.append(TempSplitToken)
                ColonSplitTokens = list()
                for CommaSplitToken in CommaSplitTokens:
                    TempSplitTokens = CommaSplitToken.split(':')
                    for SplitIndex, TempSplitToken in enumerate(TempSplitTokens):
                        if SplitIndex:
                            ColonSplitTokens.append(':')
                        if len(TempSplitToken):
                            ColonSplitTokens.append(TempSplitToken)
                PlusSplitTokens = list()
                for ColonSplitToken in ColonSplitTokens:
                    TempSplitTokens = ColonSplitToken.split('+') if ColonSplitToken[0] != '#' else [ColonSplitToken]
                    for SplitIndex, TempSplitToken in enumerate(TempSplitTokens):
                        if SplitIndex:
                            PlusSplitTokens.append('+')
                        if len(TempSplitToken):
                            PlusSplitTokens.append(TempSplitToken)
                MinusSplitTokens = list()
                for PlusSplitToken in PlusSplitTokens:
                    TempSplitTokens = PlusSplitToken.split('-') if PlusSplitToken[0] != '#' else [PlusSplitToken]
                    for SplitIndex, TempSplitToken in enumerate(TempSplitTokens):
                        if SplitIndex:
                            MinusSplitTokens.append('-')
                        if len(TempSplitToken):
                            MinusSplitTokens.append(TempSplitToken)            
                for SplitToken in MinusSplitTokens:
                    LineTokens.append(SplitToken)
                    
            #print(LineTokens)
            if Assembler.TokenType(LineTokens[0]) == Assembler.TOKEN_TYPE_IDENTIFIER:
                if LineTokens[0].upper() == 'DAT':
                    return (Assembler.LINE_TYPE_DATA if len(LineTokens) == 2 else Assembler.LINE_TYPE_INVALID, line, linenumber, LineTokens)
                elif LineTokens[0].upper() in self.InstructionToMachine:
                    return (Assembler.LINE_TYPE_INSTRUCTION, line, linenumber, LineTokens)
                elif len(LineTokens) > 1 and Assembler.TokenType(LineTokens[1]) == Assembler.TOKEN_TYPE_COLON:
                    return (Assembler.LINE_TYPE_LABEL, line, linenumber, LineTokens)
            return (Assembler.LINE_TYPE_INVALID, line, linenumber, LineTokens)
        return (Assembler.LINE_TYPE_EMPTY, line, linenumber)

    @staticmethod
    def TokenType(token):
        if len(token) == 0:
            return Assembler.TOKEN_TYPE_INVALID
        if token[0] == '$':
            if IsInt(token[1:]):
                RegNumber = int(token[1:])
                if 0 <= RegNumber and RegNumber < Assembler.REGISTER_COUNT:
                    return Assembler.TOKEN_TYPE_REGISTER
        elif token[0] == '#':
            if IsInt(token[1:]):
                return Assembler.TOKEN_TYPE_CONSTANT
        elif len(token) == 1:
            if token in ['A','I','N','Z','O','C','E']:
                return Assembler.TOKEN_TYPE_FLAG
            if token[0] == ',':
                return Assembler.TOKEN_TYPE_COMMA
            if token[0] == ':':
                return Assembler.TOKEN_TYPE_COLON
            if token[0] == '+':
                return Assembler.TOKEN_TYPE_PLUS
            if token[0] == '-':
                return Assembler.TOKEN_TYPE_MINUS
        elif token[0].isalpha():
            if token[1:].isalnum():
                return Assembler.TOKEN_TYPE_IDENTIFIER
            
        return Assembler.TOKEN_TYPE_INVALID

    @staticmethod
    def InstructionIsValid(tokens):
        Instructions2Regs = ['NOT', 'INV', 'MOV', 'ROR', 'ROL', 'SHL', 'SHR', 'JSR']
        Instructions3Regs = ['ADD', 'SUB', 'AND', 'OR', 'XOR']
        Instructions1RegConst = ['LIL', 'LIL0', 'LIL1', 'LIH']
        Instructions2RegsOptional = ['LD', 'ST']
        Instructions1Reg01 = ['LDFI', 'MOVF', 'MSRP', 'MSRF']
        
        InstructionName = tokens[0].upper()
        if InstructionName in Instructions2Regs:
            if len(tokens) != 4:
                return False
            for Index in range(1,4,2):
                if Assembler.TokenType(tokens[Index]) != Assembler.TOKEN_TYPE_REGISTER:
                    return False
            if Assembler.TokenType(tokens[2]) != Assembler.TOKEN_TYPE_COMMA:
                return False    
            return True
        elif InstructionName in Instructions3Regs:
            if len(tokens) != 6:
                return False
            for Index in range(1,6,2):
                if Assembler.TokenType(tokens[Index]) != Assembler.TOKEN_TYPE_REGISTER:
                    return False
            for Index in range(2,6,2):
                if Assembler.TokenType(tokens[Index]) != Assembler.TOKEN_TYPE_COMMA:
                    return False    
            return True
        elif InstructionName in Instructions1RegConst:
            if len(tokens) != 4:
                return False
            if Assembler.TokenType(tokens[1]) != Assembler.TOKEN_TYPE_REGISTER:
                return False
            if Assembler.TokenType(tokens[2]) != Assembler.TOKEN_TYPE_COMMA:
                return False
            ImmediateType = Assembler.TokenType(tokens[3])
            if ImmediateType != Assembler.TOKEN_TYPE_CONSTANT and ImmediateType != Assembler.TOKEN_TYPE_IDENTIFIER:
                return False
            return True
        elif InstructionName in Instructions1Reg01:
            if len(tokens) != 4:
                return False
            if Assembler.TokenType(tokens[1]) != (Assembler.TOKEN_TYPE_REGISTER if InstructionName == 'MOVEF' else Assembler.TOKEN_TYPE_FLAG):
                return False
            if Assembler.TokenType(tokens[2]) != Assembler.TOKEN_TYPE_COMMA:
                return False
            if Assembler.TokenType(tokens[3]) != Assembler.TOKEN_TYPE_CONSTANT:
                return False
            Value = RegOrDataToInt(tokens[3])
            return Value == 0 or Value == 1
        elif InstructionName in Instructions2RegsOptional:
            if len(tokens) != 4 and len(tokens) != 6:
                return False
            for Index in range(1,4,2):
                if Assembler.TokenType(tokens[Index]) != Assembler.TOKEN_TYPE_REGISTER:
                    return False
            if Assembler.TokenType(tokens[2]) != Assembler.TOKEN_TYPE_COMMA:
                return False 
            if len(tokens) == 6:
                OffsetOperand = Assembler.TokenType(tokens[4])
                if OffsetOperand != Assembler.TOKEN_TYPE_PLUS and OffsetOperand != Assembler.TOKEN_TYPE_MINUS:
                    return False 
                if Assembler.TokenType(tokens[5]) != Assembler.TOKEN_TYPE_CONSTANT:
                    return False
            return True
        elif InstructionName in ['NOP', 'SWI', 'RTI']:
            return len(tokens) == 1
        elif InstructionName == 'JMP':
            if len(tokens) != 2:
                return False
            if Assembler.TokenType(tokens[1]) != Assembler.TOKEN_TYPE_REGISTER:
                return False
            return True
        elif InstructionName == 'ADDI':
            if len(tokens) != 6:
                return False
            for Index in range(1,4,2):
                if Assembler.TokenType(tokens[Index]) != Assembler.TOKEN_TYPE_REGISTER:
                    return False
            for Index in range(2,6,2):
                if Assembler.TokenType(tokens[Index]) != Assembler.TOKEN_TYPE_COMMA:
                    return False    
            return Assembler.TokenType(tokens[5]) == Assembler.TOKEN_TYPE_CONSTANT
        elif InstructionName == 'BR':
            if Assembler.TokenType(tokens[1]) != Assembler.TOKEN_TYPE_FLAG:
                print('Expected flag')
                return False
            if Assembler.TokenType(tokens[2]) != Assembler.TOKEN_TYPE_COMMA:
                print('Expected comma')
                return False
            TargetType = Assembler.TokenType(tokens[3])   
            if TargetType != Assembler.TOKEN_TYPE_CONSTANT and TargetType != Assembler.TOKEN_TYPE_IDENTIFIER:
                return False
            return True
        return False
        
    def TranslateInstruction(self, instdata):
        InstructionTokens = instdata[3]
        if instdata[0] == Assembler.LINE_TYPE_DATA:
            DataValue = RegOrDataToInt(InstructionTokens[1])
            if Assembler.MAX_NEGATIVE_DATA_VALUE <= DataValue and DataValue <= Assembler.MAX_POSITIVE_DATA_VALUE:
                return DataValue % (Assembler.MAX_POSITIVE_DATA_VALUE + 1)
        
        Instructions2Regs = ['NOT', 'INV', 'MOV', 'ROR', 'ROL', 'SHL', 'SHR', 'JSR']
        Instructions3Regs = ['ADD', 'SUB', 'AND', 'OR', 'XOR']
        Instructions1RegConst = ['LIL', 'LIL0', 'LIL1', 'LIH']
        Instructions2RegsOptional = ['LD', 'ST']  
        
        InstructionName = InstructionTokens[0]
        ReturnValue = self.InstructionToMachine[InstructionName]
        if InstructionName in Instructions2Regs:
            ReturnValue <<= 3
            ReturnValue += RegOrDataToInt(InstructionTokens[1])
            ReturnValue <<= 3
            ReturnValue += RegOrDataToInt(InstructionTokens[3])
            return ReturnValue << 4
        elif InstructionName in Instructions3Regs:
            ReturnValue <<= 3
            ReturnValue += RegOrDataToInt(InstructionTokens[1])
            ReturnValue <<= 3
            ReturnValue += RegOrDataToInt(InstructionTokens[3])
            ReturnValue <<= 3
            ReturnValue += RegOrDataToInt(InstructionTokens[5])
            return ReturnValue << 1
        elif InstructionName in Instructions1RegConst:
            Constant = RegOrDataToInt(InstructionTokens[3])
            if InstructionName == 'LIL':
                InstructionName = 'LIL1' if (Constant >> 7) & 1 else 'LIL0'
                ReturnValue = self.InstructionToMachine[InstructionName]
            ReturnValue <<= 3
            ReturnValue += RegOrDataToInt(InstructionTokens[1])
            ReturnValue <<= 7
            if InstructionName == 'LIL0' or InstructionName == 'LIL1':
                ReturnValue += Constant & 0x7F
            else:
                ReturnValue += (Constant>>8) & 0x7F
            return ReturnValue
        elif InstructionName == 'LDFI':
            ReturnValue <<= 3
            ReturnValue += self.FlagIndices[InstructionTokens[1]]
            ReturnValue <<= 7
            ReturnValue += RegOrDataToInt(InstructionTokens[3])
            return ReturnValue
        elif InstructionName in ['MOVF', 'MSRP', 'MSRF' ]:
            Constant = RegOrDataToInt(InstructionTokens[3])
            if Constant:
                ReturnValue <<= 3
                ReturnValue += RegOrDataToInt(InstructionTokens[1])
                ReturnValue <<= 7
            else:
                ReturnValue <<= 6
                ReturnValue += RegOrDataToInt(InstructionTokens[1])
                ReturnValue <<= 4
            ReturnValue += Constant
            return ReturnValue
        elif InstructionName in Instructions2RegsOptional:
            Offset = 0
            if len(InstructionTokens) == 6:
                Multiplier = 1 if Assembler.TokenType(InstructionTokens[4]) == Assembler.TOKEN_TYPE_PLUS else -1
                Offset = (RegOrDataToInt(InstructionTokens[5]) * Multiplier) % 16
            ReturnValue <<= 3
            ReturnValue += RegOrDataToInt(InstructionTokens[1])
            ReturnValue <<= 3
            ReturnValue += RegOrDataToInt(InstructionTokens[3])
            ReturnValue <<= 4
            ReturnValue += Offset

            return ReturnValue
        elif InstructionName in ['NOP', 'SWI', 'RTI']:
            return ReturnValue << 10
        elif InstructionName == 'JMP':
            ReturnValue <<= 3
            ReturnValue += RegOrDataToInt(InstructionTokens[1])
            ReturnValue <<= 7
            return ReturnValue
        elif InstructionName == 'ADDI':
            ReturnValue <<= 3
            ReturnValue += RegOrDataToInt(InstructionTokens[1])
            ReturnValue <<= 3
            ReturnValue += RegOrDataToInt(InstructionTokens[3])
            ReturnValue <<= 4
            ReturnValue += RegOrDataToInt(InstructionTokens[5]) % 16
            return ReturnValue
        elif InstructionName == 'BR':
            OffsetTarget = RegOrDataToInt(InstructionTokens[3])
            if Assembler.MAX_NEGATIVE_BRANCH_OFFSET > OffsetTarget or OffsetTarget > Assembler.MAX_POSITIVE_BRANCH_OFFSET:
                print('Branch target on line {} is beyond maximum offset!'.format(instdata[2]))
                return -1
            ReturnValue <<= 3
            ReturnValue += self.FlagIndices[InstructionTokens[1]]
            ReturnValue <<= 7
            ReturnValue += OffsetTarget & 0x7F
            return ReturnValue
        return -1
        
    @staticmethod
    def OutputBinaryToLogisim(data,filename):
        OutStrings = list()
        RunCount = 0
        LastValue = -1
        for Value in data:
            if Value != LastValue:
                if RunCount > 3:
                    OutStrings.append('{}*{:x}'.format(RunCount,LastValue))
                else:
                    for Index in range(0, RunCount):                
                        OutStrings.append('{:x}'.format(LastValue))
                RunCount = 1
                LastValue = Value
            else:
                RunCount += 1
        if RunCount > 3:
            OutStrings.append('{}*{:x}'.format(RunCount,LastValue))
        else:
            for Index in range(0, RunCount):                
                OutStrings.append('{:x}'.format(LastValue))
        OutLines = list()
        CurrentLine = 'v2.0 raw'
        for Index, String in enumerate(OutStrings):
            if Index % 8 == 0:
                CurrentLine += '\n'
                OutLines.append(CurrentLine)
                CurrentLine = String
            else:
                CurrentLine += ' ' + String
        CurrentLine += '\n'
        OutLines.append(CurrentLine)
        with open(filename, 'w') as BinaryFile:
            for Line in OutLines:
                BinaryFile.write(Line)
        
    def Assemble(self, asmfile):
        LabelLocations = dict()
        LocationToLabels = dict()
        Instructions = list()
        MachineCodes = list()
        TargetFilename = asmfile[:-4] + '.dat' if asmfile[-4:].lower() == '.asm' else asmfile + '.dat'
        DumpFilename = asmfile[:-4] + '.dump' if asmfile[-4:].lower() == '.asm' else asmfile + '.dump'
        with open(asmfile, 'r') as AssemblyFile:
            for LineNumber, Line in enumerate(AssemblyFile):
                ParsedLine = self.ParseLine(Line, LineNumber)
                #print('{:3}: {}'.format(LineNumber, ParsedLine))
                ParsedLineType = ParsedLine[0]
                if Assembler.LINE_TYPE_EMPTY == ParsedLineType:
                    continue
                if Assembler.LINE_TYPE_INVALID == ParsedLineType:
                    print('Error on line {}, "{}"'.format(LineNumber+1, Line if Line[-1] != '\n' else Line[:-1]))
                    return False
                ParsedTokens = ParsedLine[3]
                if Assembler.LINE_TYPE_LABEL == ParsedLineType:
                    if len(ParsedTokens) != 2:
                        print('Error on line {}, "{}" unexpected token after colon'.format(LineNumber+1, Line if Line[-1] != '\n' else Line[:-1]))
                        return False
                    if ParsedTokens[0] in LabelLocations:
                        if isinstance(LabelLocations[ParsedTokens[0]],int):
                            print('Error on line {}, "{}" redefined label'.format(LineNumber+1, Line if Line[-1] != '\n' else Line[:-1]))
                            return False
                        else:
                            LabelLocation = len(Instructions)
                            if len(Instructions) not in LocationToLabels:
                                LocationToLabels[len(Instructions)] = list()
                            LocationToLabels[len(Instructions)].append(ParsedTokens[0])
                            for RelativeOffset, InstructionTokens in LabelLocations[ParsedTokens[0]]:
                                for Index in range(1,len(InstructionTokens)):
                                    if Assembler.TOKEN_TYPE_IDENTIFIER == Assembler.TokenType(InstructionTokens[Index]):
                                        if InstructionTokens[Index] == ParsedTokens[0]:
                                           InstructionTokens[Index] = '#{}'.format(LabelLocation - RelativeOffset)
                            LabelLocations[ParsedTokens[0]] = LabelLocation
                    else:
                        LabelLocations[ParsedTokens[0]] = len(Instructions)
                        if len(Instructions) not in LocationToLabels:
                            LocationToLabels[len(Instructions)] = list()
                        LocationToLabels[len(Instructions)].append(ParsedTokens[0])
                elif Assembler.LINE_TYPE_INSTRUCTION == ParsedLineType:
                    if not Assembler.InstructionIsValid(ParsedTokens):
                        print('Error on line {}, "{}" invalid instruction format'.format(LineNumber+1, Line if Line[-1] != '\n' else Line[:-1]))
                        return False
                    IsBranch = ParsedTokens[0] == 'BR'
                    for Index in range(1,len(ParsedTokens)):
                        if Assembler.TOKEN_TYPE_IDENTIFIER == Assembler.TokenType(ParsedTokens[Index]):
                            if ParsedTokens[Index] in LabelLocations:
                                if isinstance(LabelLocations[ParsedTokens[Index]], int):
                                    ParsedTokens[Index] = '#{}'.format(LabelLocations[ParsedTokens[Index]] - len(Instructions)  if IsBranch else LabelLocations[ParsedTokens[Index]])
                                else:
                                    LabelLocations[ParsedTokens[Index]].append((len(Instructions) if IsBranch else 0,ParsedTokens))
                            else:
                                LabelLocations[ParsedTokens[Index]] = [(len(Instructions) if IsBranch else 0, ParsedTokens)]
                    Instructions.append(ParsedLine)
                elif Assembler.LINE_TYPE_DATA == ParsedLineType:
                    if Assembler.TokenType(ParsedTokens[1]) != Assembler.TOKEN_TYPE_CONSTANT:
                        print('Error on line {}, "{}" expected constant'.format(LineNumber+1, Line if Line[-1] != '\n' else Line[:-1]))
                        return False
                    Instructions.append(ParsedLine)
        BinaryMemory = list()
        DumpLines = list()
        for MemLocation,Inst in enumerate(Instructions):
            MachineCode = self.TranslateInstruction(Inst)
            if 0 > MachineCode:
                print('Could not translate instruction on line {}'.format(Inst[2]))
                return False
            BinaryMemory.append(MachineCode)
            if MemLocation in LocationToLabels:
                DumpLines.append('{:04X}: {}; {}\n'.format(MemLocation, Inst[1].strip(), LocationToLabels[MemLocation][0]))
            else:
                DumpLines.append('{:04X}: {}\n'.format(MemLocation, Inst[1].strip()))
        Assembler.OutputBinaryToLogisim(BinaryMemory,TargetFilename)
        with open(DumpFilename, 'w') as OutFile:
            for Line in DumpLines:
                OutFile.write(Line)
        return True
        
    
def main():
    if 3 > len(sys.argv):
        print('Syntax Error: assemble inst2mach.csv file.asm')
        return
    SimpleAssembler = Assembler(sys.argv[1])
    if not SimpleAssembler.TranslationLoaded:
        print('Failed to load instruction code translations')
        return
    SimpleAssembler.Assemble(sys.argv[2])
    

if __name__ == '__main__':
    main()
