# Sistema Experto - Recomendador de Arquitectura

Sistema experto en Python (Experta) que recomienda stacks tecnológicos
según el contexto del proyecto: tipo, equipo, plazos, presupuesto y
requerimientos técnicos.

## Requisitos
- Python 3.8 - 3.9 (Experta no funciona bien en 3.10+)
- pip

## Instalación y ejecución

### CMD
```cmd
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
python main.py

### POWERSHELL
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py

### En caso de 2 o mas versiones de python
verificamos 3.9.X
py --list
luego en la raiz del proyecto
py -3.9 -m venv venv