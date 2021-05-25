import sys
import os
import struct
from PIL import Image
from PIL import ExifTags
from libraw.bindings import LibRaw
from libraw import *
from PySide2.QtWidgets import QDialog, QPushButton, QLabel, QListView, QApplication, QWidget, QHBoxLayout, QVBoxLayout, QAbstractItemView, QComboBox, QGridLayout, QFileDialog, QLineEdit
from PySide2.QtCore import QSize
from PySide2.QtGui import QFont, QStandardItemModel, QPixmap, QStandardItem, QIcon, Qt, QTransform
from pyexiftool import ExifTool
from datetime import datetime
from lens_exif_model import marcas, f_length, marcas_modelo, lente, lens, apertures

qt_app = QApplication(sys.argv)


class Interfaz(QWidget) :

	def __init__(self) :
		QWidget.__init__(self)

		self.screen = qt_app.primaryScreen()
		self.screen_size = self.screen.size()
		self.screen_width = self.screen_size.width()
		self.screen_height = self.screen_size.height()
		
		if self.screen_width > 1920 :
			
			self.screen_minimum_width = self.screen_width * 0.6
			self.setMinimumWidth(self.screen_minimum_width)	
		
		elif self.screen_width <= 1920 :
		
			self.screen_minimum_width = self.screen_width * 0.8
			self.setMinimumWidth(self.screen_minimum_width)
		 
		if self.screen_height > 1080 :
		
			self.screen_minimum_height = self.screen_height * 0.7
			self.setMinimumHeight(self.screen_minimum_height)	
		
		elif self.screen_height <= 1920 :
		
			self.screen_minimum_height = self.screen_height * 0.8
			self.setMinimumHeight(self.screen_minimum_height)	



		self.setWindowTitle('Manual Lens Exif')

		self.img_dir = None
	
		self.thumb_layout = QHBoxLayout()
		self.display_layout = QVBoxLayout()
		self.exif_layout = QHBoxLayout()
#		self.exif_layout.setMinimumHeight(100)

		self.font = QFont()
		self.font.setPointSize(11)

		#vista de los thumbnails
	
		self.list_view = QListView()

		self.files()

		self.dir = QPushButton("Directory")
		self.dir.clicked.connect(self.select_dir)

		
		self.thumb_layout.addWidget(self.dir)
		self.thumb_layout.addWidget(self.list_view)

		# Formulario datos exif

		self.exif_form()

		# Preview img
		self.image_display_label = QLabel()		
		self.image_display = QLabel()

		self.display_height = self.screen_minimum_height * 0.75
		self.image_display.setMinimumHeight(self.display_height)
		self.display_layout.addWidget(self.image_display_label)
		self.display_layout.addWidget(self.image_display)


		# Grilla principal

		self.grid_layout = QGridLayout()
		self.grid_layout.addLayout(self.thumb_layout, 0, 0)
		self.grid_layout.addLayout(self.display_layout, 1, 0)
		self.grid_layout.addLayout(self.exif_layout, 2, 0)
		self.setLayout(self.grid_layout)

		self.list_view.clicked.connect(self.display)
		self.list_view.activated.connect(self.display)
		
		self.list_view.clicked.connect(lambda : self.enable_disable_button(self.write, self.lente.currentText(), self.aperture.currentText(), self.image_display_label.text()))
		self.list_view.activated.connect(lambda : self.enable_disable_button(self.write, self.lente.currentText(), self.aperture.currentText(), self.image_display_label.text()))
		
		self.image_display_label.setFont(self.font)
		self.list_view.setFont(self.font)
		self.dir.setFont(self.font)
		
		
	# Habilita y deshabilita botones conforme a las variables necesarias
			
	def enable_disable_button(self, combo_widget, *args) :
		
		self.number_of_args = len(args)		
		self.combo_widget = combo_widget		
		self.arg_before = None
		
		for self.arg in args :
			
			if self.arg != '' and self.arg is not None and self.arg_before is None and self.number_of_args == 1 :			

				self.arg_before = True
			
			elif self.arg_before is False :
			
				self.arg_before = False
			
			elif self.arg != '' and self.arg is not None and self.arg_before is None and self.number_of_args != 1 :
			
				self.arg_before = True
			
			elif self.arg != '' and self.arg is not None and self.arg_before is True and self.number_of_args != 1 :

				self.arg_before = True

			else :

				self.arg_before = False

			if self.arg_before is True :
			
				combo_widget.setEnabled(True)	
			
			else: 
			
				combo_widget.setEnabled(False)		


	# Crear lente

	def new_lens_dialog(self) :
		self.new_lens_form = QDialog()
		self.new_lens_form.setWindowTitle('New Lens')
		self.new_lens_form.setFont(self.font)

		self.new_lens_form.adjustPosition(self.image_display)

		self.dialog_layout = QGridLayout()
		
		self.dialog_marca_form()
		self.dialog_model_form()
		self.dialog_focal_form()
		
				
		self.dialog_min_aperture_label = QLabel('Minimum aperture f/')
		self.dialog_min_aperture = QComboBox()
		self.dialog_min_aperture.addItem('')

		for self.min_aperture_options in apertures :

			if self.min_aperture_options >= 11 :
				self.dialog_min_aperture.addItem(str(self.min_aperture_options))


#		self.dialog_min_aperture.insertItems(0, a_min)
		
		self.dialog_max_aperture_label = QLabel('Maximum aperture f/')
		self.dialog_max_aperture = QComboBox()
		self.dialog_max_aperture.addItem('')		

		for self.max_aperture_options in apertures :

			if self.max_aperture_options <= 8 :
				self.dialog_max_aperture.addItem(str(self.max_aperture_options))

		self.dialog_min_aperture.activated.connect(lambda : self.enable_disable_button(self.dialog_add, self.dialog_marca.currentText(), self.dialog_model.currentText(), self.dialog_focal.currentText(), self.dialog_max_aperture.currentText(), self.dialog_min_aperture.currentText()))				
		self.dialog_max_aperture.activated.connect(lambda : self.enable_disable_button(self.dialog_add, self.dialog_marca.currentText(), self.dialog_model.currentText(), self.dialog_focal.currentText(), self.dialog_max_aperture.currentText(), self.dialog_min_aperture.currentText()))	
		
				
#		self.dialog_max_aperture.addItems(a_max)
		
		self.dialog_add = QPushButton('Add')
		
		self.dialog_add.setEnabled(False)
		
		self.dialog_cancel = QPushButton('Cancel')
		
		self.dialog_layout.addWidget(self.dialog_max_aperture_label, 3, 0)
		self.dialog_layout.addWidget(self.dialog_max_aperture, 3, 1)

		self.dialog_layout.addWidget(self.dialog_min_aperture_label, 4, 0)
		self.dialog_layout.addWidget(self.dialog_min_aperture, 4, 1)
				
		self.dialog_layout.addWidget(self.dialog_add, 5, 3)
		self.dialog_layout.addWidget(self.dialog_cancel, 5, 2)

		self.dialog_cancel.clicked.connect(lambda: self.close_dialog(self.new_lens_form))
		self.dialog_add.clicked.connect(self.write_add_new_lens)
		
		self.new_lens_form.setLayout(self.dialog_layout)
		self.new_lens_form.exec_()		


	#Cerrar el dialogo de form nuevo lente

	def close_dialog(self, dialog) :
		
		self.dialog = dialog
		self.dialog.close()

	# Guardar un nuevo lente en la base

	def write_add_new_lens(self) :
	
		self.marca_text = self.dialog_marca.currentText()
		self.model_text = self.dialog_model.currentText()
		self.focal_text = self.dialog_focal.currentText()
		self.focal_text = self.focal_text.replace('m', '')
		self.max_aperture_text = self.dialog_max_aperture.currentText()
		self.min_aperture_text = self.dialog_min_aperture.currentText()
		
		self.new_add_lens = lente(None, self.marca_text, self.model_text, self.focal_text, self.max_aperture_text, self.min_aperture_text)
		self.write_new_add_lens = self.new_add_lens.new_lens()

		if self.write_new_add_lens is True :
		
			self.new_add_lens.write_to_file()
			self.dialog_marca_form()
			self.dialog_model_form()		
			self.dialog_focal_form()
			self.dialog_max_aperture.setCurrentIndex(0)
			self.dialog_min_aperture.setCurrentIndex(0)
			self.lens_show(self.lente)
			self.aperture.clear()

	# formulario de marca en dialogo de nuevo lente
		
	def dialog_marca_form(self) :
		
		self.dialog_marca_label = QLabel('Brand')
		self.dialog_marca = QComboBox(self)
		self.marcas = sorted(marcas, key=lambda z: (z.upper(), z.islower()))
		self.dialog_marca.insertItems(0, self.marcas)
		self.dialog_new_marca = QPushButton('+')
		self.dialog_less_marca = QPushButton('-')
		self.dialog_marca.activated.connect(self.dialog_model_for_marca)

		self.dialog_new_marca.clicked.connect(self.add_marca)
		self.dialog_less_marca.clicked.connect(self.write_remove_marca)

		try :
			self.enable_disable_button(self.dialog_add, self.dialog_marca.currentText(), self.dialog_model.currentText(), self.dialog_focal.currentText(), self.dialog_max_aperture.currentText(), self.dialog_min_aperture.currentText())
		except :
			self.result_try = None
		
		self.dialog_marca.activated.connect(lambda : self.enable_disable_button(self.dialog_add, self.dialog_marca.currentText(), self.dialog_model.currentText(), self.dialog_focal.currentText(), self.dialog_max_aperture.currentText(), self.dialog_min_aperture.currentText()))
		
		self.dialog_layout.addWidget(self.dialog_marca_label, 0, 0)
		self.dialog_layout.addWidget(self.dialog_marca, 0, 1)
		self.dialog_layout.addWidget(self.dialog_new_marca, 0, 2)
		self.dialog_layout.addWidget(self.dialog_less_marca, 0, 3)
		self.dialog_layout.update()


	# formulario de modelo en el dialogo de nuevo lente

	def dialog_model_form(self) :
		
		
		self.dialog_model_label = QLabel('Model')
		self.dialog_model = QComboBox()
		self.dialog_new_model = QPushButton('+')
		self.dialog_less_model = QPushButton('-')
		
		self.dialog_new_model.clicked.connect(self.add_model)
		self.dialog_less_model.clicked.connect(self.write_remove_model)		
				
		try :
			self.enable_disable_button(self.dialog_add, self.dialog_marca.currentText(), self.dialog_model.currentText(), self.dialog_focal.currentText(), self.dialog_max_aperture.currentText(), self.dialog_min_aperture.currentText())
		except :
			self.result_try = None
		
		self.dialog_model.activated.connect(lambda : self.enable_disable_button(self.dialog_add, self.dialog_marca.currentText(), self.dialog_model.currentText(), self.dialog_focal.currentText(), self.dialog_max_aperture.currentText(), self.dialog_min_aperture.currentText()))
				
		self.dialog_layout.addWidget(self.dialog_model_label, 1, 0)
		self.dialog_layout.addWidget(self.dialog_model, 1, 1)
		self.dialog_layout.addWidget(self.dialog_new_model, 1, 2)
		self.dialog_layout.addWidget(self.dialog_less_model, 1, 3)
		self.dialog_layout.update()
		self.dialog_model_for_marca()

	# formulario de focal en dialogo de nuevo lente

	def dialog_focal_form(self) :
	
		self.dialog_focal_label = QLabel('Focal distance')
		self.dialog_focal = QComboBox()
		self.f_length = sorted(f_length, key=lambda v: (v.upper(), v.islower()))
		self.dialog_focal.insertItems(0, self.f_length)
		self.dialog_new_focal = QPushButton('+')
		self.dialog_less_focal = QPushButton('-')
		
		self.dialog_new_focal.clicked.connect(self.add_focal)
		self.dialog_less_focal.clicked.connect(self.write_remove_focal)	

		try :		
			self.enable_disable_button(self.dialog_add, self.dialog_marca.currentText(), self.dialog_model.currentText(), self.dialog_focal.currentText(), self.dialog_max_aperture.currentText(), self.dialog_min_aperture.currentText())

		except :
			self.result_try = None
			
		self.dialog_focal.activated.connect(lambda : self.enable_disable_button(self.dialog_add, self.dialog_marca.currentText(), self.dialog_model.currentText(), self.dialog_focal.currentText(), self.dialog_max_aperture.currentText(), self.dialog_min_aperture.currentText()))
		
		self.dialog_layout.addWidget(self.dialog_focal_label, 2, 0)
		self.dialog_layout.addWidget(self.dialog_focal, 2, 1)
		self.dialog_layout.addWidget(self.dialog_new_focal, 2, 2)
		self.dialog_layout.addWidget(self.dialog_less_focal, 2, 3)
		self.dialog_layout.update()	


	# añadir items de modelo segun la marca en dialogo de nuevo lente 

	def dialog_model_for_marca(self) :

		self.dialog_selected_marca = self.dialog_marca.currentText()
		self.dialog_model.clear()
		self.dialog_model.addItem("")		
		self.list_of_items = marcas_modelo.keys()

		self.models_ordered = []
	
		for self.dialog_key in self.list_of_items :

			self.b = marcas_modelo[self.dialog_key]['marca']
			self.c = marcas_modelo[self.dialog_key]['modelo']
			
			if self.dialog_selected_marca == self.b :
	

				self.models_ordered.append(self.c)	

		for self.model_order in sorted(self.models_ordered, key=lambda v: (v.upper(), v.islower())) :
		
			self.dialog_model.addItem(self.model_order)


	# Fromulario para añadir marca

	def add_marca(self) :

		self.dialog_layout.removeWidget(self.dialog_marca)
		self.dialog_layout.removeWidget(self.dialog_new_marca)
		self.dialog_layout.removeWidget(self.dialog_less_marca)		
		self.dialog_layout.update()
		
		self.dialog_new_marca_input_text = QLineEdit()
		self.dialog_new_marca_add = QPushButton('Add')
		
		self.dialog_new_marca_add.setEnabled(False)
		
		self.dialog_new_marca_cancel = QPushButton('Cancel')

		self.dialog_layout.addWidget(self.dialog_new_marca_input_text, 0, 1)
		self.dialog_layout.addWidget(self.dialog_new_marca_add, 0, 2)
		self.dialog_layout.addWidget(self.dialog_new_marca_cancel, 0, 3)
		self.dialog_layout.update()
		
		self.dialog_model_form()
		
		self.dialog_new_marca_add.clicked.connect(self.write_marca)
		self.dialog_new_marca_cancel.clicked.connect(self.dialog_marca_form)
		
		self.dialog_new_marca_input_text.textChanged.connect(lambda : self.enable_disable_button(self.dialog_new_marca_add, self.dialog_new_marca_input_text.text()))
		

	# Añadir marca en la base
		
	def write_marca(self) :
		
		self.marca_text = self.dialog_new_marca_input_text.text()
		self.new_lens = lente(None, self.marca_text, None, None, None, None)
		self.new_lens_new_marca = self.new_lens.new_marca()

		if self.new_lens_new_marca is True :
			self.new_lens.write_to_file()
			self.dialog_marca_form()
			self.dialog_model_form()


	# Borrar marca
 	
	def write_remove_marca(self) :
		self.dialog_selected_marca = self.dialog_marca.currentText()

		if self.dialog_selected_marca != "" and self.dialog_selected_marca != " " :
			self.new_lens = lente(None, self.dialog_selected_marca, None, None, None, None)
			self.new_lens_remove_marca = self.new_lens.remove_marca()
			self.new_lens.write_to_file()
			self.dialog_marca_form()
			self.dialog_model_form()
		

	# cambio a formulario para añadir un modelo en dialogo de nuevo lente 
	
	def add_model(self) :
	
		self.dialog_layout.removeWidget(self.dialog_model)
		self.dialog_layout.removeWidget(self.dialog_new_model)
		self.dialog_layout.removeWidget(self.dialog_less_model)		
		self.dialog_layout.update()
		
		self.dialog_new_model_input_text = QLineEdit()
		self.dialog_new_model_add = QPushButton('Add')
		self.dialog_new_model_cancel = QPushButton('Cancel')
		
		self.dialog_new_model_add.setEnabled(False)

		self.dialog_layout.addWidget(self.dialog_new_model_input_text, 1, 1)
		self.dialog_layout.addWidget(self.dialog_new_model_add, 1, 2)
		self.dialog_layout.addWidget(self.dialog_new_model_cancel, 1, 3)
		self.dialog_layout.update()
				
		self.dialog_selected_marca_index = self.dialog_marca.currentIndex()
		self.dialog_marca_form()
		self.dialog_marca.setCurrentIndex(self.dialog_selected_marca_index)
		
		self.dialog_new_model_add.clicked.connect(self.write_model)
		self.dialog_new_model_cancel.clicked.connect(self.dialog_model_form)

		self.dialog_new_model_input_text.textChanged.connect(lambda : self.enable_disable_button(self.dialog_new_model_add, self.dialog_new_model_input_text.text(), self.dialog_marca.currentText()))


	#añadir modelo en la base

	def write_model(self) :
		
		self.dialog_selected_marca = self.dialog_marca.currentText()
		self.model_text = self.dialog_new_model_input_text.text()
		self.new_lens = lente(None, self.dialog_selected_marca, self.model_text, None, None, None)
		self.new_lens_new_model = self.new_lens.new_modelo()

		if self.new_lens_new_model is True :
		
			self.new_lens.write_to_file()
			self.dialog_selected_marca_index = self.dialog_marca.currentIndex()
			self.dialog_marca_form()
			self.dialog_marca.setCurrentIndex(self.dialog_selected_marca_index)
			self.dialog_model_form()
			self.dialog_model_for_marca()

	#borrar modelo de la base

	def write_remove_model(self) :

		self.dialog_selected_marca = self.dialog_marca.currentText()
		self.dialog_selected_model = self.dialog_model.currentText()

		if self.dialog_selected_marca != "" and self.dialog_selected_marca != " " and self.dialog_selected_model != "" and self.dialog_selected_model != " ":

			self.new_lens = lente(None, self.dialog_selected_marca, self.dialog_selected_model, None, None, None)
			self.new_lens.remove_modelo()
			self.new_lens.write_to_file()
			self.dialog_selected_marca_index = self.dialog_marca.currentIndex()
			self.dialog_marca_form()
			self.dialog_marca.setCurrentIndex(self.dialog_selected_marca_index)
			self.dialog_model_form()
			self.dialog_model_for_marca()

		else :
		
			print("Select the model to remove")


	#Cambio a formulario de añadir focal en dialogo de nuevo lente
	
	def add_focal(self) :
		
		self.dialog_layout.removeWidget(self.dialog_focal)
		self.dialog_layout.removeWidget(self.dialog_new_focal)
		self.dialog_layout.removeWidget(self.dialog_less_focal)		
		self.dialog_layout.update()
		
		self.dialog_new_focal_input_text = QLineEdit()
		self.dialog_new_focal_add = QPushButton('Add')
		self.dialog_new_focal_cancel = QPushButton('Cancel')

		self.dialog_new_focal_add.setEnabled(False)

		self.dialog_layout.addWidget(self.dialog_new_focal_input_text, 2, 1)
		self.dialog_layout.addWidget(self.dialog_new_focal_add, 2, 2)
		self.dialog_layout.addWidget(self.dialog_new_focal_cancel, 2, 3)
		self.dialog_layout.update()
		
		self.dialog_new_focal_add.clicked.connect(self.write_focal)
		self.dialog_new_focal_cancel.clicked.connect(self.dialog_focal_form)
		self.dialog_new_focal_input_text.textChanged.connect(lambda : self.enable_disable_button(self.dialog_new_focal_add, self.dialog_new_focal_input_text.text()))		
	
	
	#Añadir focal en la base
	
	def write_focal(self) :

		self.focal_text = self.dialog_new_focal_input_text.text()
		self.focal_text = self.focal_text.replace('m', '')
		
		self.new_lens = lente(None, None, None, self.focal_text, None, None)
		self.new_lens_new_focal = self.new_lens.new_focal()

		if self.new_lens_new_focal is True :
		
			self.new_lens.write_to_file()
			self.dialog_focal_form()
		
			
			
	#Borrar focal en la base	
		
	def write_remove_focal(self) :

		self.dialog_selected_focal = self.dialog_focal.currentText()
		self.dialog_selected_focal = self.dialog_selected_focal.replace('m', '')

		if self.dialog_selected_focal != "" and self.dialog_selected_focal != " " :

			self.new_lens = lente(None, None, None, self.dialog_selected_focal, None, None)
			self.new_lens_remove_focal = self.new_lens.remove_focal()
			self.new_lens.write_to_file()
			self.dialog_focal_form()	


 	# Datos para el exif de una foto

	def exif_form(self) :
		
		self.lente_label = QLabel('  Lens : ')
		self.lente_label.setMaximumWidth(70)
		self.lente = QComboBox(self)
		self.lens_show(self.lente)

		self.aperture_label = QLabel('  Aperture : f/')
		self.aperture_label.setMaximumWidth(100)
		self.aperture = QComboBox(self)

		self.write = QPushButton("Write Exif")

		self.lente.activated.connect(self.apertures_show)	
		self.lente.activated.connect(lambda : self.enable_disable_button(self.write, self.lente.currentText(), self.aperture.currentText(), self.image_display_label.text()))
		self.aperture.activated.connect(lambda : self.enable_disable_button(self.write, self.lente.currentText(), self.aperture.currentText(), self.image_display_label.text()))

		self.write.setEnabled(False)

		self.write.clicked.connect(self.write_exif)

		self.new_lens = QPushButton("New Lens")
		self.new_lens.clicked.connect(self.new_lens_dialog)

		self.remove_lens = QPushButton("Remove Lens")
		self.remove_lens.clicked.connect(self.remove_lens_dialog)

		self.lente_label.setFont(self.font)
		self.lente.setFont(self.font)
		self.aperture.setFont(self.font)
		self.aperture_label.setFont(self.font)
		self.write.setFont(self.font)
		self.new_lens.setFont(self.font)
		self.remove_lens.setFont(self.font)

		self.exif_layout.addWidget(self.lente_label)		
		self.exif_layout.addWidget(self.lente)
		self.exif_layout.addWidget(self.aperture_label)
		self.exif_layout.addWidget(self.aperture)
		self.exif_layout.addWidget(self.write)
		self.exif_layout.addWidget(self.new_lens)
		self.exif_layout.addWidget(self.remove_lens)


	# Añade o cambia los datos de lente y apertura en el exif de la img

	def write_exif(self) :
	
		self.image_for_exif = self.img_dir + '/' + self.complete_image_name
		
#		self.lens_for_exif = self.lente.currentText()
		self.lens_aperture_for_exif = self.aperture.currentText()
		self.lens_selected = self.lente.currentData()
		self.max_aperture_for_exif = lens[self.lens_selected]['max_aperture']	
		self.focal_for_exif = lens[self.lens_selected]['focal']
		self.focal_for_exif = self.focal_for_exif.replace('m', '')
		self.lens_brand_for_exif = lens[self.lens_selected]['marca']
		self.lens_model_for_exif =  lens[self.lens_selected]['modelo']
		self.lens_for_exif = self.lens_model_for_exif + ' ' + self.focal_for_exif + 'mm' + '  f/' + self.max_aperture_for_exif
				
		if self.lens_for_exif != '' and self.lens_for_exif != '' and self.lens_for_exif is not None and self.lens_aperture_for_exif != '' and self.lens_aperture_for_exif != ' ' and self.lens_aperture_for_exif is not None :
		
			self.a = "-overwrite_original_in_place"
			self.b = "-P"
			self.c = "-m"
			self.d = "-LensType="+self.lens_for_exif
			self.e = "-LensModel="+self.lens_for_exif
			self.f = "-Lens="+self.lens_for_exif
			self.g = "-ApertureValue="+self.lens_aperture_for_exif
			self.h = "-FNumber="+self.lens_aperture_for_exif
			self.i = "-FocalLength="+self.focal_for_exif
			self.j = "-MaxApertureValue"+self.max_aperture_for_exif
			self.k = "-LensMake="+self.lens_brand_for_exif
		
			self.a_e = self.a.encode()
			self.b_e = self.b.encode()
			self.c_e = self.c.encode()
			self.d_e = self.d.encode()
			self.e_e = self.e.encode()
			self.f_e = self.f.encode()
			self.g_e = self.g.encode()
			self.h_e = self.h.encode()
			self.i_e = self.i.encode()
			self.j_e = self.j.encode()
			self.k_e = self.k.encode()
			self.image_for_exif = self.image_for_exif.encode()
			
			with ExifTool() as et :
				et.execute(self.a_e, self.b_e, self.c_e, self.d_e, self.e_e, self.f_e, self.g_e, self.h_e, self.i_e, self.j_e, self.k_e, self.image_for_exif)
			self.display(self.index_selected_image)


	#formulario para borrar un lente

	def remove_lens_dialog(self) : 

		self.remove_lens_dialog_widget = QDialog()
		self.remove_lens_dialog_widget.setWindowTitle('Remove Lens')
		self.remove_lens_dialog_widget.setFont(self.font)		
		
		self.remove_lens_dialog_widget.adjustPosition(self.image_display)
			
		self.remove_lens_dialog_layout = QHBoxLayout()
		self.lenses_remove_combobox_label = QLabel('Lens : ')
		self.lenses_remove_combobox = QComboBox()
		
		self.lens_remove_button = QPushButton('Remove')
		self.lens_remove_button.setEnabled(False)

		self.lens_remove_cancel_button = QPushButton('Cancel')		

		self.lenses_remove_combobox.activated.connect(lambda: self.enable_disable_button(self.lens_remove_button, self.lenses_remove_combobox.currentText()))
		self.lens_remove_button.clicked.connect(self.remove_lens_from_base)
		self.lens_remove_cancel_button.clicked.connect(lambda: self.close_dialog(self.remove_lens_dialog_widget))
		
		self.remove_lens_dialog_widget.setLayout(self.remove_lens_dialog_layout)

		self.lens_show(self.lenses_remove_combobox)

		self.remove_lens_dialog_layout.addWidget(self.lenses_remove_combobox_label)		
		self.remove_lens_dialog_layout.addWidget(self.lenses_remove_combobox)
		self.remove_lens_dialog_layout.addWidget(self.lens_remove_button)
		self.remove_lens_dialog_layout.addWidget(self.lens_remove_cancel_button)		

		self.remove_lens_dialog_widget.exec_()

	# Borrar lente de la base

	def remove_lens_from_base(self) :

		self.remove_lens_index = self.lenses_remove_combobox.currentData()
		self.new_lens = lente(self.remove_lens_index, None, None, None, None, None)
		self.new_lens_remove_lens = self.new_lens.remove_lens()

		if self.new_lens_remove_lens is True :

			self.lens_show(self.lenses_remove_combobox)
			self.lens_show(self.lente)
			self.apertures_show()

	# muestra los lentes de la base en combobox

	def lens_show(self, combobox) :
	
		self.combobox = combobox
		self.combobox.clear()

		self.lenses_order = []

		for self.lens_object in lens :
	
			self.lens_object_brand = lens[self.lens_object]['marca']
			self.lens_object_model = lens[self.lens_object]['modelo']
			self.lens_object_focal = lens[self.lens_object]['focal']			
			self.lens_object_min_aperture = lens[self.lens_object]['min_aperture']			
			self.lens_object_max_aperture =	lens[self.lens_object]['max_aperture']
		
			if self.lens_object_brand == '' or self.lens_object_brand is None :
	
				self.lens_object_show = ''
		
			else :		
		
				self.lens_object_show = self.lens_object_brand + ' ' + 	self.lens_object_model + ' ' + self.lens_object_focal + ' f/' + self.lens_object_max_aperture
						
			self.lenses_order.append([self.lens_object_show, self.lens_object])
			
		for self.lens_comp in sorted(self.lenses_order, key=lambda v: v[0].lower()) :
			
			self.lens_comp_lens = self.lens_comp[0]
			self.lens_comp_index =	self.lens_comp[1]

			self.combobox.addItem(self.lens_comp_lens, self.lens_comp_index)			
			
		
	#muestra las aperturas correspondientes a cada lente 
	
	def apertures_show(self) : 
	
		self.lens_selected = self.lente.currentData()

		if self.lens_selected is None :
		
			self.aperture.addItem('')
		
		else :
			self.lens_object_min_aperture = lens[self.lens_selected]['min_aperture']
			self.lens_object_max_aperture =	lens[self.lens_selected]['max_aperture']
			self.aperture.clear()
			self.aperture.addItem('')
			
			for self.available_aperture in apertures :

				if self.lens_object_min_aperture != '' or self.lens_object_min_aperture != '' :
			
					if self.available_aperture >= float(self.lens_object_max_aperture) and self.available_aperture <= float(self.lens_object_min_aperture) :

						self.aperture.addItem(str(self.available_aperture))
	

	# Mostrar preview de la img

	def display(self, index) :
		
		self.index_selected_image = index
		self.complete_image_name = str(self.list_view.model().itemData(index)[0])
		self.pre_url = os.path.splitext(os.path.basename(self.complete_image_name))[0]
		self.pre_url = str(self.pre_url)
		self.url = self.thumb_dir + '/' + self.pre_url + '.jpg'
		
		self.orientation(self.url)
		self.imagen = self.pixmap
		self.imagen = self.imagen.scaledToHeight(self.display_height)
		self.image_display.setPixmap(self.imagen)
		self.display_layout.setAlignment(Qt.AlignCenter)
		
		self.exif_raw_image = self.img_dir + '/' + self.complete_image_name
		
		with ExifTool() as et :
			self.exif_from_raw_make = str(et.get_tag('EXIF:Make', self.exif_raw_image))
			self.exif_from_raw_model = str(et.get_tag('EXIF:Model', self.exif_raw_image))
			self.exif_from_raw_lens_make = str(et.get_tag('EXIF:LensMake', self.exif_raw_image))
			self.exif_from_raw_lens_model = str(et.get_tag('EXIF:LensModel', self.exif_raw_image))
			self.exif_from_raw_lens_focal = str(et.get_tag('EXIF:FocalLength', self.exif_raw_image))
				
			self.exif_from_raw_expossure = et.get_tag('EXIF:ExposureTime', self.exif_raw_image)
			
			if 	self.exif_from_raw_expossure < 1 :
				
				self.exif_from_raw_expossure = '1/' + str(round(1 / et.get_tag('EXIF:ExposureTime', self.exif_raw_image)))
		
			else :
			
				self.exif_from_raw_expossure = str(round(et.get_tag('EXIF:ExposureTime', self.exif_raw_image)))
		
			self.exif_from_raw_aperture = str(et.get_tag('EXIF:FNumber', self.exif_raw_image))	
		
			
			if self.exif_from_raw_aperture == 'None' or self.exif_from_raw_aperture == '' :
		
				self.exif_from_raw_aperture = str(et.get_tag('EXIF:ApertureValue', self.exif_raw_image))
				
				if self.exif_from_raw_aperture == 'None' or self.exif_from_raw_aperture == '' :
				
					self.exif_from_raw_aperture = ''
				else :
				
					self.exif_from_raw_aperture = str(round(et.get_tag('EXIF:ApertureValue', self.exif_raw_image), 1))
				
			else :

				self.exif_from_raw_aperture = str(round(et.get_tag('EXIF:FNumber', self.exif_raw_image), 1))					
				
			self.exif_from_raw_iso = str(et.get_tag('EXIF:ISO', self.exif_raw_image))			

#			self.exif_from_raw_time = str(et.get_tag('EXIF:DateTimeOriginal', self.exif_raw_image))
						
			self.exif_from_raw_time = et.get_tag('EXIF:DateTimeOriginal', self.exif_raw_image)
			
			self.exif_from_raw_time = datetime.strptime(self.exif_from_raw_time, "%Y:%m:%d %H:%M:%S")
			
			self.exif_from_raw_time = str(self.exif_from_raw_time.day) + '/' + str(self.exif_from_raw_time.month) + '/' + str(self.exif_from_raw_time.year)
			
		self.display_label_content = self.exif_from_raw_make + '  ' + self.exif_from_raw_model + ' - ' + self.exif_from_raw_lens_make + '  ' + self.exif_from_raw_lens_model + '   ' + self.exif_from_raw_time + '  ' + self.exif_from_raw_expossure + 's ' + ' @ ' + ' f/ ' + self.exif_from_raw_aperture + ',  ' + 'ISO  ' + self.exif_from_raw_iso
		
		self.image_display_label.setText(self.display_label_content)
		

	# Obtener la imagen corregida en cuanto a la orientación vertical u horizontal, url es el os.path a la imagen

	def orientation(self, url) :
	
		self.pixmap = QPixmap(url)
		self.exifData = {}
		self.exif_img = Image.open(url)
		
		try :

			self.exifDataRaw = self.exif_img._getexif()

			for tag, value in self.exifDataRaw.items():
			
				self.decodedTag = ExifTags.TAGS.get(tag, tag)
				self.exifData[self.decodedTag] = value
				self.img_orientation = self.exifData.get('Orientation')

			if self.img_orientation == 8 :

				self.pixmap = self.pixmap.transformed(QTransform().rotate(270))

			elif self.img_orientation == 6 :

				self.pixmap = self.pixmap.transformed(QTransform().rotate(90))

			elif self.img_orientation == 6 :

				self.pixmap = self.pixmap.transformed(QTransform().rotate(90))
		except:

			print('Error al procesar el archivo')


	# Seleccionar directorio

	def select_dir(self) :
		
		self.directory = str(QFileDialog.getExistingDirectory(self, "Directory", ''))

		if self.directory != '' or self.directory is not None :
			
			self.img_dir = self.directory
			self.thumb_dir = self.img_dir + "/.exif_thumb"
			
		else :

			print("Invalid directory")
	
		self.files()
		self.image_display.clear()
		self.image_display_label.clear()

		self.enable_disable_button(self.write, self.lente.currentText(), self.aperture.currentText(), self.image_display_label.text())
	# Thumbnails

	def files(self) :

		self.icon_height = self.screen_minimum_height * 0.1
		self.list_view_height = self.screen_minimum_height * 0.14
#		self.list_view.setFlow(QListView.LeftToRight)
		self.list_view.setMaximumHeight(self.list_view_height)
		self.list_view.setMinimumHeight(self.list_view_height)		
#		self.list_view.setHorizontalScrollMode(QListView.ScrollPerPixel)
		self.list_view.setWrapping(0)
		self.list_view.setViewMode(QListView.IconMode)
#		self.list_view.setResizeMode(QListView.Adjust)
		self.list_view.setResizeMode(QListView.Fixed)
		self.list_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.list_view.setIconSize(QSize(self.icon_height * 2, self.icon_height))
		self.list_view.setMovement(QListView.Static)
		self.list_view.setModel(QStandardItemModel())

		if self.img_dir is not None :

			for self.img in sorted(os.listdir(self.img_dir), key=lambda v: (v.upper(), v[0].islower())) :

				self.formats = [".3fr", ".ari", ".arw", ".srf", ".sr2", ".braw", ".crw", ".cr2", ".cr3", ".cap", ".iiq", ".eip", ".dcs", ".dcr", ".drf", ".k25", ".kdc", ".dng", ".erf", ".fff", ".gpr", ".mef", ".mdc", ".mos", ".mrw", ".nef", ".nrw", ".orf", ".pef", ".ptx", ".pxn", ".R3D", ".raf", ".raw", ".rw2", ".rwl", ".rwz", ".srw", ".x3f", ".3FR", ".ARI", ".ARW", ".SRF", ".SR2", ".BRAW", ".CRW", ".CR2", ".CR3", ".CAP", ".IIQ", ".EIP", ".DCS", ".DCR", ".DRF", ".K25", ".KDC", ".DNG", ".ERF", ".FFF", ".GPR", ".MEF", ".MDC", ".MOS", ".MRW", ".NEF", ".NRW", ".ORF", ".PEF", ".PTX", ".PXN", ".R3D", ".RAF", ".RAW", ".RW2", ".RWL", ".RWZ", ".SRW", ".X3F"]

				for self.format in self.formats :

					if self.img.endswith(self.format) :

						if not os.path.exists(self.thumb_dir) :

							os.mkdir(self.thumb_dir)

						self.img_complete_name = self.img
						self.img_path = os.path.join(self.img_dir, self.img)
						self.img_name = os.path.splitext(os.path.basename(self.img_path))[0]
						self.thumb_path = os.path.join(self.thumb_dir, self.img_name) + '.jpg'	
						self.thumb_name = os.path.splitext(os.path.basename(self.thumb_path))[0]
				
						if not os.path.exists(self.thumb_path) :
					
							self.file_name_thumb = self.thumb_path.encode('ascii')
							self.file_name = self.img_path.encode('ascii')
							self.libraw  = LibRaw()
							self.raw = self.libraw.libraw_init(0)
							try :
								self.libraw.libraw_open_file(self.raw, self.file_name)
								self.libraw.libraw_unpack_thumb(self.raw)
								self.libraw.libraw_dcraw_thumb_writer(self.raw, self.file_name_thumb)
								self.libraw.libraw_close(self.raw)
							except :
								pass

						if os.path.exists(self.img_path) and os.path.exists(self.thumb_path):
	
							self.orientation(self.thumb_path)
							self.item = QStandardItem(QIcon(self.pixmap), self.img_complete_name)
							#self.item = QStandardItem(QIcon(self.pixmap), self.thumb_name)
							self.list_view.model().appendRow(self.item)
		
		else :

			print("Invalid directory")
			
	#corre la aplicación		

	def run(self):
		# Show the form
		self.show()
        # Run the qt application
		qt_app.exec_()
 
# Create an instance of the application window and run it
app = Interfaz()
app.run()

