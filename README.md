# Redes_Bravais_3D

Aplicación para la visualización 3D de redes de Bravais.

## Descripción

Este proyecto permite visualizar estructuras cristalinas en 3D mediante una interfaz gráfica.

Se han utilizado las siguientes tecnologías:

- **PySide6** para la interfaz gráfica, incluyendo botones, sliders y otros controles.
- **PyVista** para la generación y visualización de figuras en 3D.
- **PyVistaQt** como integración entre Qt y PyVista.
- **PyInstaller** para la futura generación de un archivo ejecutable.

Si se desea ejecutar el proyecto en un entorno local, en lugar de usar el ejecutable, se necesita lo siguiente:

## Requisitos

- Tener **Python 3** instalado en el sistema.
- Se recomienda ejecutar el proyecto dentro de un **entorno virtual**.

## Instalación

Desde el directorio del proyecto, ejecuta los siguientes comandos en la consola:

### 1. Crear el entorno virtual

```
python -m venv venv
```

### 2. Activar el entorno virtual

```
venv\Scripts\activate
```

### 3. Instalar las dependencias del proyecto

```
pip install PySide6 pyvista pyvistaqt
```

### 4. Instalar PyInstaller (opcional)

```
pip install pyinstaller
```

## Verificación rápida

```
python -c "from PySide6.QtWidgets import QApplication; print('Qt OK')"
python -c "import pyvista as pv; print(pv.__version__)"
```

## Ejecución

```
python redes_bravais_withSolids.py
```

## Notas

- La carpeta `venv` no debe subirse a GitHub.
- Cada usuario debe crear su propio entorno virtual localmente.
- El archivo principal del proyecto debe estar fuera de la carpeta `venv`.
