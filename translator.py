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
		self.allocated_temp = -1 
		self.constant = (_ast.Num,_ast.Name)
	def visit_BinOp(self, node):
		op = self.get_op(node.op)
		if type(node.left) in self.constant:
			left = self.visit(node.left)
		else:
			left = self.sub_expression(node.left)
			
		if type(node.right) in self.constant:
			right = self.visit(node.right)
		else:
			right = self.sub_expression(node.right)
			
		return "{} {},{}".format(op, left, right)
	def visit_Num(self, node):
		return str(node.n)
	def visit_Name(self, node):
		return self.generate_variable(node)
	def visit_Assign(self, node):
		self.output.write(";[assign {}]\n".format(ast.dump(node)))
		operation = ast.NodeVisitor.visit(self, node.value)
		var = self.generate_variable(node.targets[0])
		self.output.write("{} {}\n".format(var, operation))
		self.store_variable(node.targets[0])
	def visit_Expr(self, node):
		ast.NodeVisitor.generic_visit(self, node)
	def visit_Call(self, node):
		if node.func.id == "print":
			self.generate_print(node)
		else:
			self.output.write("{} = call i32 @{} (%{})\n".format(self.create_temp(), node.func.id, node.args[0].id))
	def generic_visit(self, node):
		if type(node) is not _ast.Module:
			self.output.write("[{}]".format(ast.dump(node)))
		ast.NodeVisitor.generic_visit(self, node)
	def get_op(self, op):
		if type(op) is _ast.Add:
			return "add i32"
		elif type(op) is _ast.Sub:
			return "sub i32 "
		elif type(op) is _ast.Div:
			return "sdiv i32 "
		elif type(op) is _ast.Mult:
			return "mul i32 "
		else:
			raise Exception("unsupported operator " +str(type(op)))
	def generate_variable(self, node):
		if node.id not in self.allocated_objects:
			self.allocated_objects[node.id] = 0
			self.output.write("%{} = alloca i32\n".format(node.id))
			return "{} = ".format(self.current_variable(node))
		if type(node.ctx) is _ast.Load:
			self.load_variable(node)
			return "{}".format(self.current_variable(node))
		elif type (node.ctx) is _ast.Store:
			self.allocated_objects[node.id] += 1
			return "{} = ".format(self.current_variable(node))
			##self.store_variable(node)
			
	def load_variable(self, node):
		self.allocated_objects[node.id] += 1
		self.output.write("%{}.{} = load i32* %{}\n".format(node.id, self.allocated_objects[node.id], node.id))
	def current_variable(self, node):
		return "%{}.{}".format(node.id, self.allocated_objects[node.id])
	def store_variable(self, node):
		self.output.write("store i32 %{}.{},i32* %{}\n".format(node.id, self.allocated_objects[node.id], node.id))
	def create_temp(self):
		self.allocated_temp += 1
		return "%{}".format(self.allocated_temp)
	def sub_expression(self, node):
			operation = self.visit(node)
			var = self.create_temp()
			self.output.write("{} = {}\n".format(var, operation))
			return var
	def close(self):
		self.output.write("""ret i32 0
}		\n""")
		self.output.close()
	def generate_print(self, node):
		self.load_variable(node.args[0])
		self.output.write("{} = call i32 (i8*, ...)* @printf(i8* noalias getelementptr inbounds ([4 x i8]* @.print_int, i64 0, i64 0), i32 {}) nounwind \n".format(self.create_temp(),self.current_variable(node.args[0])))

