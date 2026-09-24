# Conciliador Bancário Rigoroso

Aplicação Full-Stack de Conciliação Bancária 100% em memória.

## Stack
- **Backend**: Python 3.11 + FastAPI + Uvicorn
- **PDF Parsing**: pdfplumber
- **Frontend**: React 19 + Vite + Tailwind CSS v4 + TanStack Table
- **Deploy**: Railway (1 serviço unificado)

## Rodando localmente

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend (dev)
```bash
cd frontend
npm install
npm run dev
```

O frontend em dev aponta para `http://localhost:8000` via proxy do Vite.

## Deploy no Railway
O projeto está configurado para deploy automático no Railway via `railway.json`.
O build compila o frontend e sobe o FastAPI servindo os assets estáticos.
