#!/usr/bin/python3
import ast, sys
import translator
filename = sys.argv[1]
outputfile = filename.strip(".py")+".ll"
visitor = translator.MyVisitor(outputfile)
fp = open(filename)
sourcecode = fp.read() 
a = ast.parse(sourcecode, filename)
visitor.visit(a)
visitor.close()
assembler = open(outputfile)
print (assembler.read())
