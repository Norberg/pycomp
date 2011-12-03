import ast, _ast

class MyVisitor(ast.NodeVisitor):
	def __init__(self, outputfile):
		self.output = open(outputfile, 'w')
		self.output.write("""declare i32 @printf(i8* noalias, ...) nounwind
@.print_int = private constant [4 x i8] c"%d\n\00", align 1 ; <[4 x i8]*> [#uses=1]

define i32 @main() nounwind {
entry:
		""")
	def visit_BinOp(self, node):
		self.output.write(self.getOp(node.op))
		self.visit(node.left)
		self.output.write(',')
		self.visit(node.right)
		self.output.write('\n')
	def visit_Num(self, node):
		self.output.write(str(node.n))
	def visit_Name(self, node):
		self.output.write("%")
		self.output.write(node.id)
	def visit_Assign(self, node):
		ast.NodeVisitor.generic_visit(self, node)
	def visit_Expr(self, node):
		ast.NodeVisitor.generic_visit(self, node)
	def visit_Call(self, node):
		if node.func.id == "print":
			self.generate_print(node)
		else:
			self.output.write("call i32 @{} (%{})\n".format(node.func.id, node.args[0].id))
	def generic_visit(self, node):
		if type(node) is not _ast.Module:
			self.output.write("[{}]".format(ast.dump(node)))
		ast.NodeVisitor.generic_visit(self, node)
	def getOp(self, op):
		if type(op) is _ast.Add:
			return " = add i32 "
	def generate_print(self, node):
		self.output.write("call i32 (i8*, ...)* @printf(i8* noalias getelementptr inbounds ([4 x i8]* @.print_int, i64 0, i64 0), i32 %{}) nounwind \n".format(node.args[0].id))
	def close(self):
		self.output.write("""ret i32 0
}		""")
		self.output.close()

