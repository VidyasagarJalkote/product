# 🐘 Production CRUD Application with PostgreSQL & Dump Deployment

A production-ready Full Stack CRUD Application designed for DevOps engineers to practice developing locally with PostgreSQL, exporting data with the **Dump Method (`pg_dump`)**, and deploying the project & database onto a production server.

---

## 📌 Architecture & Features

- **Backend**: Python FastAPI with RESTful endpoints (`/api/employees`, `/api/stats`, `/health`, `/ready`)
- **Database**: PostgreSQL 18 with connection pooling, table schemas, indexes, and automated seeding
- **Frontend**: Clean single-page responsive dashboard (HTML5, CSS3, modern Vanilla JS)
- **DevOps Tools**: 
  - Database Dump Workshop built right into the UI
  - Automated PowerShell & Bash export/restore scripts
  - Multi-stage production `Dockerfile`
  - `docker-compose.yml` for running full stack with single command

---

## 🚀 Quick Start (Running Locally)

### Option 1: Fast Start via PowerShell
Open PowerShell in this project folder and run:
```powershell
.\start.ps1
```

### Option 2: Manual Start
1. Ensure your PostgreSQL service is running:
   ```powershell
   wsl sudo service postgresql start
   ```
2. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
3. Start the application:
   ```powershell
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

Open your browser at:
- **Application UI**: [http://localhost:8000](http://localhost:8000)
- **Interactive API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 📝 Pre-Loaded Data & Sample Data to Add

### Pre-Loaded in Database on Startup:
1. **Alex Johnson** (`alex.j@company.com`) - Senior DevOps Engineer - \$95,000 - Active
2. **Priya Sharma** (`priya.s@company.com`) - Cloud Infrastructure Architect - \$115,000 - Active
3. **Marcus Chen** (`marcus.c@company.com`) - Full Stack Developer - \$88,000 - Active
4. **Elena Rostova** (`elena.r@company.com`) - Site Reliability Engineer - \$102,000 - Active

### Sample Records to Add via the UI:
Click **"+ Add Employee"** (or use the one-click preset buttons on the UI banner) to add these:

| Name | Email | Role | Department | Salary | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **David Kim** | `david.k@company.com` | Kubernetes Specialist | DevOps & Cloud | \$98,000 | Active |
| **Aisha Patel** | `aisha.p@company.com` | Security & Compliance Engineer | Security | \$105,000 | Active |
| **Carlos Gomez** | `carlos.g@company.com` | QA Automation Engineer | QA & Testing | \$82,000 | Active |
| **Sophia Rossi** | `sophia.r@company.com` | Cloud Cost Optimization Lead | DevOps & Cloud | \$110,000 | Remote |

---

## 🎯 The Core Learning Objective: The Database Dump & Deploy Method

When developing on a local laptop, your database is stored on your local disk (`localhost:5432`). When you are ready to deploy your application to a staging or production server (e.g. AWS EC2, DigitalOcean, or an on-premise Linux VM), you need both your **code** and your **database data** on the remote server.

Here is the exact production workflow:

### Step 1: Create the Local Database Dump
A database dump exports your schema (tables, constraints, sequences) and data (rows) into a single `.sql` script.

**Using the included script:**
```powershell
.\scripts\export_dump.ps1
```
*Or using the CLI directly:*
```bash
pg_dump -U postgres -h localhost -p 5432 -d devops_db --clean --if-exists -F p -f devops_db_dump.sql
```
*Or directly click **"Download devops_db_dump.sql"** in the web UI!*

> **Flag Explanations:**
> - `-U postgres`: The database user
> - `-h localhost`: Host where database resides
> - `-d devops_db`: Target database name
> - `--clean --if-exists`: Adds `DROP TABLE IF EXISTS` so it can cleanly overwrite existing tables on production without duplicate key errors
> - `-F p`: Plain text SQL format (human-readable and pipeable)
> - `-f devops_db_dump.sql`: Output filename

---

### Step 2: Transfer the Dump & Code to the Production Server
Copy your application files and the SQL dump to your production server:

```bash
# 1. Transfer the database dump file
scp devops_db_dump.sql ubuntu@your-server-ip:/home/ubuntu/

# 2. Transfer project code (or clone from GitHub)
scp -r * ubuntu@your-server-ip:/home/ubuntu/app/
```

---

### Step 3: Restore Database Dump on Production Server
SSH into your remote server:
```bash
ssh ubuntu@your-server-ip
```

1. Ensure PostgreSQL is installed on the server:
   ```bash
   sudo apt update && sudo apt install -y postgresql postgresql-contrib
   sudo service postgresql start
   ```

2. Create the production database:
   ```bash
   sudo -u postgres psql -c "CREATE DATABASE devops_db;"
   ```

3. Restore the dump file using `psql`:
   ```bash
   sudo -u postgres psql -d devops_db -f /home/ubuntu/devops_db_dump.sql
   ```
   *All your tables, schema, constraints, sequences, and local records are now restored into production!*

4. Verify restored data:
   ```bash
   sudo -u postgres psql -d devops_db -c "SELECT id, name, role, salary FROM employees;"
   ```

---

### Step 4: Run Application on Production

Configure your production `.env` with the production database credentials:
```bash
cd /home/ubuntu/app
cp .env.example .env
nano .env
```

Install requirements and run via systemd or docker:
```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 🐳 Alternative: Deploy Entire Stack with Docker Compose

If your production server has Docker installed, you can deploy both PostgreSQL and the app together:

```bash
# 1. Export dump
.\scripts\export_dump.ps1

# 2. Start stack on server
docker compose up -d --build
```
The `docker-compose.yml` mounts `devops_db_dump.sql` directly into `/docker-entrypoint-initdb.d/init.sql`, which automatically restores your local data when PostgreSQL starts for the first time!

---

## 🛑 Stop Application
```powershell
.\stop.ps1
```
