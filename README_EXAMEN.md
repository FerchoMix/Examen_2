# Sistema web - Taller Mecánico (Flask-AppBuilder)

## Mejoras incluidas
- Corrección de importaciones para Flask-AppBuilder reciente.
- Corrección de textos con tildes y ortografía.
- Inicio del sistema redirigido al login si el usuario no ha iniciado sesión.
- Después del login se muestra un dashboard interactivo.
- Dashboard con indicadores, gráficos y tabla de órdenes recientes.
- 3 reportes mejorados visualmente.
- 3 gráficas con Chart.js.
- Imágenes llamativas desde internet en dashboard, reportes y gráficas.

## Ejecución
```powershell
python -m venv venv
.\venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
$env:FLASK_APP="run.py"
python -m flask fab create-db
python semilla.py
python -m flask run --debug
```
