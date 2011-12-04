#!/usr/bin/python3
import ast, sys, os
import translator
filename = sys.argv[1]
llfile = filename.strip(".py")+".ll"
visitor = translator.MyVisitor(llfile)
fp = open(filename)
sourcecode = fp.read() 
a = ast.parse(sourcecode, filename)
visitor.visit(a)
visitor.close()
bcfile = filename.strip(".py")+".bc"
sfile = filename.strip(".py")+".s"
os.system("llvm-as -f {}".format(llfile))
os.system("llc -f {}".format(bcfile))
os.system("gcc {}".format(sfile))
os.system("rm {} {}".format(bcfile, sfile))
