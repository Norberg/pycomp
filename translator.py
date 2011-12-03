import ast, _ast

class MyVisitor(ast.NodeVisitor):
	def __init__(self, outputfile):
		self.output = open(outputfile, 'w')
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
		self.output.write("{Expr}")
		ast.NodeVisitor.generic_visit(self, node)
	def visit_Call(self, node):
		self.output.write("{Call}")
		ast.NodeVisitor.generic_visit(self, node)
	def generic_visit(self, node):
		self.output.write("")
		self.output.write("[" + type(node).__name__ +"]")
		ast.NodeVisitor.generic_visit(self, node)
	def getOp(self, op):
		if type(op) is _ast.Add:
			return " = add i32 "
	def close(self):
		self.output.close()

