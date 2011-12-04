#!/usr/bin/python3
import difflib, glob, os, sys

for test in glob.glob("test/*.py"):
	failed = False
	os.system("python3 {} > test/output.reference".format(test))
	os.system("./compile.py {}".format(test))
	os.system("./a.out > test/output")
	diff = difflib.context_diff(open("test/output.reference").readlines(),
	       open("test/output").readlines(), "reference", "testcase")
	for d in diff:
		if not failed:
			print("Testcase: {} failed!".format(test))
			failed = True
		print(d, end='')
	if not failed:
		print("Testcase: {} succeeded!".format(test))
