class Entidade:
	
	def __init__(self,nome,tags):
		self.set_nome(nome)
		self.set_tags(tags)
		
	def set_nome(self,nome):
		self._nome = nome
		
	def set_tags(self,tags):
		self._tags = set(tags)
		
	def __str__(self):
		return f"{self._nome}, tags: {self._tags}"
	
	def contem(self, outra):
		return outra._tags.issubset(self._tags)
