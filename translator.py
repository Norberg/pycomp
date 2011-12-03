import ast, _ast

class MyVisitor(ast.NodeVisitor):
	def __init__(self, outputfile):
		self.output = open(outputfile, 'w')
		self.output.write("""declare i32 @printf(i8* noalias, ...) nounwind
@.print_int = private constant [4 x i8] c"%d\n\00", align 1 ; <[4 x i8]*> [#uses=1]

define i32 @main() nounwind {
entry:
		""")
		self.allocated_objects = dict()
	def visit_BinOp(self, node):
		self.output.write(self.get_op(node.op))
		self.visit(node.left)
		self.output.write(',')
		self.visit(node.right)
		self.output.write('\n')
	def visit_Num(self, node):
		self.output.write(str(node.n))
	def visit_Name(self, node):
		self.output.write(self.current_variable(node))
	def visit_Assign(self, node):
		self.output.write(";[assign {}]\n".format(ast.dump(node)))
		self.generate_variable(node.targets[0])
		ast.NodeVisitor.visit(self, node.value)
		self.store_variable(node.targets[0])
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
	def get_op(self, op):
		if type(op) is _ast.Add:
			return " add i32 "
		elif type(op) is _ast.Sub:
			return " sub i32 "
		elif type(op) is _ast.Div:
			return " sdiv i32 "
		elif type(op) is _ast.Mult:
			return " mul i32 "
		else:
			raise Exception("unsupported operator " +str(type(op)))
	def generate_variable(self, node):
		if node.id not in self.allocated_objects:
			self.allocated_objects[node.id] = 0
			self.output.write("%{} = alloca i32\n".format(node.id))
			self.output.write("{} = ".format(self.current_variable(node)))
			return
		if type(node.ctx) is _ast.Load:
			self.load_variable(node)
		elif type (node.ctx) is _ast.Store:
			self.store_variable(node)
			
	def load_variable(self, node):
		self.allocated_objects[node.id] += 1
		self.output.write("%{}.{} = load i32* %{}\n".format(node.id, self.allocated_objects[node.id], node.id))
	def current_variable(self, node):
		return "%{}.{}".format(node.id, self.allocated_objects[node.id])
	def store_variable(self, node):
		self.output.write("store i32 %{}.{},i32* %{}\n".format(node.id, self.allocated_objects[node.id], node.id))

	def close(self):
		self.output.write("""ret i32 0
}		""")
		self.output.close()
	def generate_print(self, node):
		self.load_variable(node.args[0])
		self.output.write("call i32 (i8*, ...)* @printf(i8* noalias getelementptr inbounds ([4 x i8]* @.print_int, i64 0, i64 0), i32 {}) nounwind \n".format(self.current_variable(node.args[0])))

