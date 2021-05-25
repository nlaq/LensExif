from lens_exif_data import lens, marcas, f_length, marcas_modelo, apertures


class lente:
	def __init__(self, r_id, r_marca, r_modelo, r_focal, r_apertura, r_apertura_min):
	
		self.validate(r_id, r_marca, r_modelo, r_focal, r_apertura, r_apertura_min)

	def validate(self, r_id, r_marca, r_modelo, r_focal, r_apertura, r_apertura_min) :

		if r_id is None or r_id == '' or r_id == ' ' :
			r_id = None

		if r_marca is None or r_marca == '' or r_marca == ' ' :
			r_marca = None

		if r_modelo is None or r_modelo == '' or r_modelo == ' ' :
			r_modelo = None

		if r_focal is None or r_focal == '' or r_focal == ' ' :
			r_focal = None
		else :	
			try :
				int(r_focal)
			except : 	
				r_focal = None
		
		if r_apertura is None or r_apertura == '' or r_apertura == ' ' :
			r_apertura = None		
		if r_apertura_min is None or r_apertura_min == '' or r_apertura_min == ' ' :
			r_apertura_min = None	

		self.id = r_id
		self.marca = r_marca
		self.modelo = r_modelo
		self.focal = r_focal
		self.apertura = r_apertura
		self.apertura_min = r_apertura_min

# crear una marca

	def new_marca(self):
		if self.marca is not None and self.marca not in marcas:
			marcas.append(self.marca)
			result = True
		else:
			result = "error"
			print("Escriba la marca del lente o verifique que no existe ya")
		return result
		
# borrar una marca

	def remove_marca(self):
			
		if self.marca is not None and self.marca in marcas:
			marcas.remove(self.marca)
		else :
			print("error")
		return

# crear una distancia focal

	def new_focal(self):
		if self.focal is not None :
			if 'm' not in self.focal and self.focal + 'mm' not in f_length :
				f_length.append(self.focal + 'mm')
				result =True
			else :
				print("Escriba el número de la distancia focal en mm o verifique que no existe ya")
				result = "error"	
		else :
			print("Escriba el número de la distancia focal en mm")
			result = "error"
		return result
		
# borrar una distancia focal

	def remove_focal(self):
		if self.focal is not None :
			if 'm' not in self.focal and self.focal + 'mm' in f_length :
				f_length.remove(self.focal + 'mm')
			else :
				print("Escriba el número de la distancia focal en mm y verifique que existe")	
		else :
			print("Escriba el número de la distancia focal en mm")
		return


# Crear un modelo

	def new_modelo(self) :

		x = False
		if self.marca is not None and self.modelo is not None :

			self.list_of_marcas_modelo = marcas_modelo.keys()
			for self.key in self.list_of_marcas_modelo :
				self.z = marcas_modelo[self.key]['marca']
				self.y = marcas_modelo[self.key]['modelo']
				if self.marca == self.z and self.modelo == self.y or x == True:
					x = True
				else :
					x = False
		if self.marca is not None and self.modelo is not None and x == False:
			id = int(max(marcas_modelo.keys())) + 1
			new = { id : { "marca" : self.marca, "modelo" : self.modelo}}
			marcas_modelo.update(new)
			result=True 
		else :
			result = "error"
			print("Escoja la marca y escriba el modelo del lente")
		return result

# Borrar un modelo


	def remove_modelo(self) :
		x = False
		for key, value in marcas_modelo.items() :
			if self.marca in str(value) and self.modelo in str(value) and x == False:
				x = key
		if x != False :
			id = x
			marcas_modelo.pop(id)
		else :
			print("Seleccione una marca y modelo para eliminar")	
		return		


# Crear lente

	def new_lens(self) :
		
		y = False
		for value in lens.items() :
			if self.marca in str(value) and self.modelo in str(value) and self.focal in str(value) and self.apertura in str(value) or y == True:
				y = True
			else :
				y = False
		if self.marca is not None and self.modelo is not None and self.focal is not None and self.apertura is not None and self.apertura_min is not None and y == False:
			id = int(max(lens.keys())) + int(1)
			new = { id : { "marca" : self.marca, "modelo" : self.modelo, "focal" : self.focal+'mm', "max_aperture" : self.apertura, "min_aperture" : self.apertura_min}}
			lens.update(new)
			result = True
		else :
			print("Escoja la marca, modelo, distncia focal y apertura máxima del lente")
			result = "error"
		return result

# Borrar lente

	def remove_lens(self) :

		lens.pop(self.id)
		result = True
		return result

# escribir a la base

	def write_to_file(self):
		base = open('lens_exif_data.py', 'w')
		base.write('marcas = ' + str(marcas) + '\r')
		base = open('lens_exif_data.py', 'a')
		base.write('f_length = ' + str(f_length) + '\r')
		base.write('marcas_modelo = ' + str(marcas_modelo) + '\r')
		base.write('lens = ' + str(lens) + '\r')
		base.write('apertures = ' + str(apertures) + '\r')
		return




#nuevo_lente = lente(id, marca, modelo, focal, apertura)
#nuevo_lente.new_marca()
#nuevo_lente.remove_marca()
#nuevo_lente.write_to_file()
#nuevo_lente.new_modelo()
#nuevo_lente.remove_modelo()
#nuevo_lente.new_focal()
#nuevo_lente.remove_focal()
#nuevo_lente.new_lens()
#nuevo_lente.remove_lens()
#nuevo_lente.write_to_file()

