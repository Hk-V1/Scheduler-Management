# Scheduler Dashboard

A full-stack scheduler management system built with FastAPI backend and Next.js frontend, supporting multiple databases and deployment-ready for Render and Vercel.

## Features

- 🚀 **FastAPI Backend** with APScheduler for job management
- ⚛️ **Next.js Frontend** with TypeScript and Tailwind CSS
- 🗄️ **Multi-Database Support** (PostgreSQL, MySQL, MSSQL, MongoDB)
- 📊 **Real-time Statistics** and execution logs
- 🔄 **Job Management** (pause, resume, delete schedulers)
- 📈 **Interactive Charts** for job statistics
- 🚢 **Production Ready** with Docker support
- ☁️ **Cloud Deployment** ready for Render (backend) and Vercel (frontend)

## Job Types Supported

- Email Notifications
- Data Backup
- Report Generation
- API Calls
- File Cleanup
- Custom Jobs

## Frequency Types

- **Cron Expression** - Unix cron syntax with timezone support
- **Interval** - Run every X seconds/minutes/hours/days
- **Date** - Run once at a specific date and time

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Database (PostgreSQL, MySQL, MSSQL, or MongoDB)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file from `.env.example` and configure your database:
```bash
cp .env.example .env
```

5. Run the backend:
```bash
python main.py
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env.local` file:
```bash
cp .env.local.example .env.local
```

4. Run the frontend:
```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

## Docker Setup

Run the entire stack with Docker Compose:

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- FastAPI backend on port 8000
- Next.js frontend on port 3000

## Database Configuration

### PostgreSQL (Recommended)
```env
DATABASE_TYPE=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=scheduler_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
```

### MySQL
```env
DATABASE_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=scheduler_db
MYSQL_USER=root
MYSQL_PASSWORD=password
```

### MongoDB
```env
DATABASE_TYPE=mongodb
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=scheduler_db
```

## Deployment

### Backend (Render)

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python main.py`
5. Add environment variables from `.env.example`
6. Create a PostgreSQL database and link it

### Frontend (Vercel)

1. Connect your GitHub repository to Vercel
2. Set root directory to `frontend`
3. Add environment variable: `NEXT_PUBLIC_API_URL=https://your-backend.render.com`
4. Deploy

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Environment Variables

### Backend
- `DATABASE_TYPE` - Database type (postgresql, mysql, mssql, mongodb)
- `DATABASE_URL` - Full database connection string (optional)
- `ENV` - Environment (development, production)
- `SECRET_KEY` - Secret key for the application
- `ALLOWED_ORIGINS` - CORS allowed origins

### Frontend
- `NEXT_PUBLIC_API_URL` - Backend API URL

## Project Structure

```
scheduler-dashboard/
├── README.md
├── .gitignore
├── .env.example
├── docker-compose.yml
│
├── frontend/                   # Next.js Frontend
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── app/
│   ├── components/
│   └── lib/
│
├── backend/                    # FastAPI Backend
│   ├── requirements.txt
│   ├── main.py
│   ├── scheduler.py
│   ├── database.py
│   ├── models.py
│   └── crud.py
│
└── docs/
    └── api_endpoints.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details
