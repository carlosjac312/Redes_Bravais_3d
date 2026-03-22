import sys
import pyvista as pv
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QSlider, QWidget, QVBoxLayout, QCheckBox, QPushButton
from pyvistaqt import QtInteractor

def clean_tri(m): #Preprocesado para que corra bien
    return m.triangulate().clean(tolerance=1e-6)

class MainWindow(QMainWindow):
    def __init__(self):
        self.figura_actual = "SC" # Variable para controlar qué figura se muestra actualmente
        self.esquinas = [(sx * 1, sy * 1, sz * 1)
                for sx in (+1, -1)
                for sy in (+1, -1)
                for sz in (+1, -1)]
        self.caras = [
            (0, 0, 1),
            (0, 0, -1),
            (0, 1, 0),
            (0, -1, 0),
            (1, 0, 0),
            (-1, 0, 0),
            ]
        
        super().__init__() #Hereda de QMainWindow para crear la ventana principal (frame)
        self.setWindowTitle("Prueba1")
        self.r = 1.0114
        #Creción de la ventana
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.vtk = QtInteractor(central)
        layout.addWidget(self.vtk) # visor 3D

        #Crear esferas para cada tipo de red
        cornersSC = self.crear_esferas_corners(1.0114)
        cornersBCC = self.crear_esferas_corners(0.88)
        cornersFCC = self.crear_esferas_corners(0.72)

        center_sphere = clean_tri(pv.Sphere(radius=0.88, center=(0, 0, 0), theta_resolution=60, phi_resolution=60)) # esfera central para BCC

        face_spheres = self.crear_esferas_caras(0.72) # esferas para las caras de FCC

        #
        self.sc_huecos = self.crear_huecos(cornersSC)
        self.bcc_huecos = self.crear_huecos(cornersBCC)
        self.fcc_huecos = self.crear_huecos(cornersFCC + face_spheres)

        self.sc_relleno = self.actor_huecos(self.sc_huecos)
        self.bcc_relleno = self.actor_huecos(self.bcc_huecos)
        self.fcc_relleno = self.actor_huecos(self.fcc_huecos)

        self.sc_corners_actors = self.crear_actores(cornersSC, (1.0, 0.0, 0.0), True) # SC
        self.bcc_corners_actors = self.crear_actores(cornersBCC, (0.0, 1.0, 1.0), False) # BCC
        self.fcc_corners_actors = self.crear_actores(cornersFCC, (0.0, 1.0, 0.0), False) # FCC

        self.face_actors = self.crear_actores(face_spheres, (1.0, 1.0, 0.0), False) # Solo mostrar las esferas de las caras para FCC

        self.bcc_center_sphere = self.vtk.add_mesh(center_sphere, color="blue", line_width=2)
        self.bcc_center_sphere.SetVisibility(False) # Solo mostrar la esfera central para FCC

        #Tools
        
        row1 = QHBoxLayout()
        layout.addLayout(row1)

        self.cb = QCheckBox("Mostrar huecos")
        row1.addWidget(self.cb)
        self.cb.toggled.connect(self.toogle_huecos)

        rstBtn = QPushButton("Reset figure")
        row1.addWidget(rstBtn)
        rstBtn.clicked.connect(self.reseteatomos) # Resetear posiciones de los átomos al hacer click en el botón

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(-1, 10)
        self.slider.setValue(-1)
        self.slider.valueChanged.connect(self.mover_atomos)
        layout.addWidget(self.slider)
        
        #Crear Fila para los botones
        row2 = QHBoxLayout()
        layout.addLayout(row2)
        
        #Añadir boton
        btnSC = QPushButton("SC")
        row2.addWidget(btnSC)

        btnBCC = QPushButton("BCC")
        row2.addWidget(btnBCC)

        btnFCC = QPushButton("FCC")
        row2.addWidget(btnFCC)

        #Conectar cada botón a una figura diferente (SC, BCC, FCC)
        btnSC.clicked.connect(lambda: self.mostrar_red("SC")) # SC
        btnBCC.clicked.connect(lambda: self.mostrar_red("BCC")) # BCC
        btnFCC.clicked.connect(lambda: self.mostrar_red("FCC")) # FCC

        # Estado inicial: checkbox desmarcado
        self.cb.setChecked(False)

    def toogle_huecos(self, estado):
        if estado:
            if self.figura_actual == "SC":
                self.sc_relleno.SetVisibility(True)
                self.bcc_relleno.SetVisibility(False)
                self.fcc_relleno.SetVisibility(False)
                self.hide_spheres(self.sc_corners_actors)
                self.bcc_center_sphere.SetVisibility(False) #Solo mostrar la esfera central para FCC
            elif self.figura_actual == "BCC":
                self.bcc_relleno.SetVisibility(True)
                self.sc_relleno.SetVisibility(False)
                self.fcc_relleno.SetVisibility(False)
                self.hide_spheres(self.bcc_corners_actors)
                self.bcc_center_sphere.SetVisibility(True) #Solo mostrar la esfera central para FCC
            elif self.figura_actual == "FCC":
                self.fcc_relleno.SetVisibility(True)
                self.sc_relleno.SetVisibility(False)
                self.bcc_relleno.SetVisibility(False)
                self.hide_spheres(self.fcc_corners_actors)
                self.hide_spheres(self.face_actors)
                self.bcc_center_sphere.SetVisibility(False) #Solo mostrar la esfera central para FCC
        else:
            self.sc_relleno.SetVisibility(False)
            self.bcc_relleno.SetVisibility(False)
            self.fcc_relleno.SetVisibility(False)
            if self.figura_actual == "SC":
                self.show_spheres(self.sc_corners_actors)
            elif self.figura_actual == "BCC":
                self.show_spheres(self.bcc_corners_actors)
            elif self.figura_actual == "FCC":
                self.show_spheres(self.fcc_corners_actors)
                self.show_spheres(self.face_actors)

    def mostrar_red(self, tipo):
        self.reseteatomos() # Resetear posiciones antes de mostrar la nueva figura
        self.figura_actual = tipo
        if not self.cb.isChecked(): # Si los huecos están activados, actualizar la visibilidad de los huecos según la figura seleccionada        
            if tipo == "SC":
                self.show_spheres(self.sc_corners_actors)
                self.hide_spheres(self.bcc_corners_actors)
                self.hide_spheres(self.fcc_corners_actors)
                self.hide_spheres(self.face_actors)
                self.bcc_center_sphere.SetVisibility(False) #Solo mostrar la esfera central para FCC

            elif tipo == "FCC":
                self.hide_spheres(self.sc_corners_actors)
                self.hide_spheres(self.bcc_corners_actors)
                self.show_spheres(self.fcc_corners_actors)
                self.show_spheres(self.face_actors)
                self.bcc_center_sphere.SetVisibility(False) #Solo mostrar la esfera central para FCC

            elif tipo == "BCC":
                self.hide_spheres(self.sc_corners_actors)
                self.show_spheres(self.bcc_corners_actors)
                self.hide_spheres(self.fcc_corners_actors)
                self.hide_spheres(self.face_actors)
                self.bcc_center_sphere.SetVisibility(True) #Solo mostrar la esfera central para FCC

            else:
                print("Tipo no válido")
        
        else:
            self.toogle_huecos(self.cb.isChecked()) # Actualizar la visibilidad de los huecos según el estado del checkbox


    def crear_esferas_corners(self, radio):
        cornersSC = [
            clean_tri(pv.Sphere(radius=radio, center=pos,
                                theta_resolution=60, phi_resolution=60))
            for pos in self.esquinas
        ]

        return cornersSC
    
    def hide_spheres(self, actores):
        for actor in actores:
            actor.SetVisibility(False)
    
    def show_spheres(self, actores):
        for actor in actores:
            actor.SetVisibility(True)

    def crear_esferas_caras(self, radio):
        face_spheres = [
            clean_tri(pv.Sphere(radius=radio, center=face,
                                theta_resolution=60, phi_resolution=60))
            for face in self.caras
        ]

        return face_spheres

    #Creación de actores a partir de array de esferas, con color y visibilidad especificados
    def crear_actores(self, meshes, color, visible):
        actores = []

        for mesh in meshes:
            actor = self.vtk.add_mesh(mesh, color=color, line_width=2)
            actor.SetVisibility(visible)
            actores.append(actor)

        return actores
    
    def crear_huecos(self, esferas):
        L = 2.3 #Tamaño del cubo, ajustar a gusto
        cube = clean_tri(pv.Cube(center=(0, 0, 0), x_length=L, y_length=L, z_length=L))
        
        # Boolean difference
        cutter = esferas[0].copy()
        for s in esferas[1:]:
            cutter = cutter.merge(s, merge_points=False)
        cutter = cutter.clean(tolerance=1e-6)
        carved = cube.boolean_difference(cutter)
        return carved
    
    def actor_huecos(self, hueco):
        # Cubo "carved" (INICIAL: invisible)
        cube_actor = self.vtk.add_mesh(hueco, color="lightgray", opacity=0.5)
        cube_actor.SetVisibility(False)
        return cube_actor
    
    #Mover esferas con el slider
    def mover_atomos(self, valor):
        if self.figura_actual == "SC":
            self.mover_sc_bcc(valor, self.sc_corners_actors)
        elif self.figura_actual == "BCC":
            self.mover_sc_bcc(valor, self.bcc_corners_actors)
        elif self.figura_actual == "FCC":
            self.mover_fcc(valor)
    
    def mover_sc_bcc(self, s, actores):
        for actor, (x, y, z) in zip(actores, self.esquinas):
            actor.SetPosition(x * (1 + s), y * (1 + s), z * (1 + s))
        self.vtk.render()

    def mover_fcc(self, s):
        for actor, (x, y, z) in zip(self.fcc_corners_actors, self.esquinas):
            actor.SetPosition(x * (1 + s), y * (1 + s), z * (1 + s))

        for actor, (x, y, z) in zip(self.face_actors, self.caras):
            actor.SetPosition(x * (1 + s), y * (1 + s), z * (1 + s))

        self.vtk.render()

    #Resetear todo
    def reseteatomos(self):
        self.slider.setValue(-1)
        if self.figura_actual == "SC":
            for actor in self.sc_corners_actors:
                actor.SetPosition(0, 0, 0)
        elif self.figura_actual == "BCC":
            for actor in self.bcc_corners_actors:
                actor.SetPosition(0, 0, 0)
        elif self.figura_actual == "FCC":
            for actor in self.fcc_corners_actors:
                actor.SetPosition(0, 0, 0)
            for actor in self.face_actors:
                actor.SetPosition(0, 0, 0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.resize(900, 700)
    w.show()
    sys.exit(app.exec())