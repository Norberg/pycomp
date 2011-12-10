#!/usr/bin/python3
import ast, sys, os
import translator
filename = sys.argv[1]
binfile=filename.strip(".py")
llfile = binfile+".ll"
visitor = translator.MyVisitor(llfile)
fp = open(filename)
sourcecode = fp.read() 
a = ast.parse(sourcecode, filename)
visitor.visit(a)
visitor.close()
bcfile = binfile+".bc"
optfile = binfile+".opt"
sfile = binfile+".s"
os.system("llvm-as {}".format(llfile))
os.system("opt -mem2reg {} > {}".format(bcfile,optfile))
os.system("mv {} {}".format(optfile,bcfile))
os.system("llc {}".format(bcfile))
os.system("gcc {} -o {}".format(sfile, binfile))
os.system("mkdir debug 2>/dev/null")
for f in(bcfile, sfile, llfile):
	os.system("mv {} debug/".format(f))
#os.system("rm {} {} {}".format(bcfile, sfile, llfile))
