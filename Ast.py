class generic():
	def __init__(self):
		self.id = "empty"
		self.type = "none"

class temp(generic):
	pass
class id(generic):
	pass
class operation():
	def __init__(self):
		self.type = "none"
		self.assign = "none"
		self.op = "none"
		self.left = "none"
		self.right = "none"
	def __str__(self):
		return "{} = {} {} {}, {}\n".format(self.assign, self.op, self.type, self.left, self.right)
