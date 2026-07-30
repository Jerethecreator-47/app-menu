# GastroFlow

Plataforma de gestión gastronómica. La Fase 1 establece estructura Flask, persistencia, autenticación y el panel de administración.

## Inicio local

En la terminal integrada de VS Code, dentro de esta carpeta:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
flask --app run.py db init
flask --app run.py db migrate -m "fundacion inicial"
flask --app run.py db upgrade
flask --app run.py seed-superadmin
flask --app run.py run --debug
```

Abrir `http://127.0.0.1:5000/login` e ingresar con el usuario creado. No subir `.env` al repositorio.
