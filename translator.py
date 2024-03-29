import ast, _ast
import Ast
from constants import datatype


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
		if type(node.left) in self.constant:
			left = self.visit(node.left)
		else:
			left = self.sub_expression(node.left)
			
		if type(node.right) in self.constant:
			right = self.visit(node.right)
		else:
			right = self.sub_expression(node.right)
		return self.create_arithmetric(node.op, left, right)	

	def visit_Num(self, node):
		num =  Ast.id()
		num.id = node.n
		num.type = self.get_datatype(num.id)
		return num

	def visit_Name(self, node):
		return self.generate_variable(node, datatype.i32) #TODO: fix datatype

	def visit_Assign(self, node):
		operation = ast.NodeVisitor.visit(self, node.value)
		var = self.generate_variable(node.targets[0], operation.type)
		operation.assign = var.id
		self.output.write(str(operation))
		self.store_variable(node.targets[0], operation.type)

	def visit_Expr(self, node):
		ast.NodeVisitor.generic_visit(self, node)

	def visit_Call(self, node):
		# atm we only support one argument to functions
		if type(node.args[0]) in self.constant:
			arg1 = self.visit(node.args[0])
		else:
			arg1 = self.sub_expression(node.args[0])
		if node.func.id == "print":
			self.generate_print(arg1)
		else:
			self.output.write("{} = call i32 @{} (%{})\n".format(self.create_temp(datatype.i32).id, node.func.id, arg1.id))

	def generic_visit(self, node):
		ast.NodeVisitor.generic_visit(self, node)

	def create_arithmetric(self, op, left, right):
		operation = Ast.operation()
		operation.type = self.get_opertype(left, right)
		operation.op = self.get_op(op)
		operation.left = left.id
		operation.right = right.id
		return operation

	def get_op(self, op):
		if type(op) is _ast.Add:
			return "add"
		elif type(op) is _ast.Sub:
			return "sub"
		elif type(op) is _ast.FloorDiv:
			return "sdiv"
		elif type(op) is _ast.Mult:
			return "mul"
		elif type(op) is _ast.Div:
			return "sdiv"
		else:
			raise Exception("unsupported operator " +str(type(op)))

	
	def get_opertype(self, *variables):
		"""returns the highest prio type of supplied variables 1: double 2: int32"""
		opertype = None
		for var in variables:
			if var.type == datatype.i32:
				if opertype != datatype.double:
					opertype = var.type 
			elif var.type == datatype.double:
				opertype = var.type
			else:
				raise Exception("unsupported datatype: {} is {}".format(str(var.id), var.type))
		return opertype
	def get_datatype(self, value):
		if type(value) is int:
			return datatype.i32
		elif type(value) is float:
			return datatype.double
		else:
			raise Exception("unsupported datatype: {} is {}".format(str(value), type(value)))
	
	def generate_variable(self, node, datatype):
		if node.id not in self.allocated_objects:
			self.allocated_objects[node.id] = 0
			self.output.write("%{} = alloca i32\n".format(node.id))
			return self.current_variable(node, datatype)
		if type(node.ctx) is _ast.Load:
			self.load_variable(node)
			return self.current_variable(node, datatype)
		elif type (node.ctx) is _ast.Store:
			self.allocated_objects[node.id] += 1
			return self.current_variable(node, datatype)
			
	def load_variable(self, node):
		self.allocated_objects[node.id] += 1
		self.output.write("%{}.{} = load i32* %{}\n".format(node.id, self.allocated_objects[node.id], node.id))

	def current_variable(self, node,datatype):
		variable = Ast.id()
		variable.id =  "%{}.{}".format(node.id, self.allocated_objects[node.id])
		variable.type = datatype
		return variable

	def store_variable(self, var, type):
		self.output.write("store {0} %{1}.{2},{0}* %{3}\n".format(type,var.id, self.allocated_objects[var.id], var.id))

	def create_temp(self, type):
		self.allocated_temp += 1
		temp = Ast.temp()
		temp.id = "%{}".format(self.allocated_temp)
		temp.type = type
		return temp

	def sub_expression(self, node):
		operation = self.visit(node)
		var = self.create_temp(operation.type)
		operation.assign = var.id
		self.output.write(str(operation))
		return var

	def close(self):
		self.output.write("""ret i32 0
}		\n""")
		self.output.close()

	def generate_print(self, arg1):
		self.output.write("{} = call i32 (i8*, ...)* @printf(i8* noalias getelementptr inbounds ([4 x i8]* @.print_int, i64 0, i64 0), i32 {}) nounwind \n".format(self.create_temp(datatype.i32).id,arg1.id))

