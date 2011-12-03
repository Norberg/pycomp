default: run

run: assembly
	lli sample.bc
build: assembly
	llc -f sample.bc
	gcc sample.s
	./a.out

assembly:
	./compiler.py sample.py
	llvm-as -f sample.ll
