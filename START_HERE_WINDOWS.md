# Start Here — Windows

## Terminal 1: Backend
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Terminal 2: Frontend
```powershell
cd frontend
npm install
npm run dev
```

Open: http://localhost:5173

If PowerShell blocks virtual-environment activation, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
then activate the environment again.
