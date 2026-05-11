# ShieldOps - DevOps-Enabled Disaster Response Simulation

**Team ShieldOps**
- **Manya Ravishankar** – 1MS23CS227
- **Kushi Kaveramma K S** – 1MS23CS095

[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen?style=for-the-badge&logo=render)](https://shieldops-eiqm.onrender.com/)

---

## 🚀 Project Overview
**ShieldOps** is a comprehensive disaster management simulation and decision intelligence platform. It empowers emergency responders and planners to simulate various disaster scenarios (Floods, Earthquakes, Fires, etc.), evaluate risks using a context-aware scoring engine, and receive AI-powered actionable recommendations.

The project is built with a **DevOps-first mindset**, featuring fully automated CI/CD pipelines, container orchestration, multi-layered security scanning, and proactive monitoring.

## ⚠️ Problem Statement
In the immediate aftermath of a disaster, decision-makers often lack clear, data-driven insights into resource allocation and priority areas. Existing systems are often siloed, lacking the integration of real-time situational updates and automated security assurance. ShieldOps solves this by providing a unified, secure, and resilient intelligence system that grows more effective with each simulation.

## ✨ Key Features
- **Multi-Hazard Simulation:** Support for 8 distinct disaster types with location-aware parameters.
- **Explainable Risk Scoring:** A weighted intelligence engine that accounts for medical, water/food, logistics, and emergency resource gaps.
- **Resilient Multi-Provider AI:** Fail-safe integration with **Google Gemini**, **OpenRouter**, and **Ollama** for generating detailed response plans.
- **Interactive Geospatial View:** Leaflet-based map integration for precise disaster location tagging.
- **Situation Re-evaluation:** Compare original assessments with post-intervention data to track situational improvement.
- **Intelligence Insights:** A learning engine that analyzes historical patterns to provide predictive response trends.
- **Health & Metrics:** Native support for Prometheus scraping and system health monitoring.

## 🛠️ Tech Stack
- **Backend:** Flask (Python 3.12), SQLAlchemy (SQLite)
- **Frontend:** Vanilla HTML5, CSS3 (Glassmorphism UI), JavaScript (ES6)
- **Maps:** Leaflet.js (OpenStreetMap)
- **AI Engine:** Google Gemini, OpenRouter (Llama 3.1/Gemma), and Ollama (Local)
- **Containerization:** Docker, Docker Compose
- **Monitoring:** Prometheus, Grafana
- **Testing:** Pytest

## 🛡️ DevOps & Security Pipeline
The project features a robust **GitHub Actions CI/CD pipeline** with the following quality gates:

1.  **Build & Unit Testing:** Automated execution of 65+ test cases using `pytest`.
2.  **SAST (Static Analysis):** Code quality and security checks using `Semgrep`.
3.  **SCA (Dependency Scanning):** Auditing of Python packages for known vulnerabilities via `Safety`.
4.  **FS Scan:** Container filesystem and configuration scanning using `Trivy`.
5.  **DAST (Dynamic Analysis):** Automated web application vulnerability scanning using `OWASP ZAP`.

## 📊 Monitoring Setup
- **Prometheus:** Scrapes application metrics (Request counts, latency, health status) from `/metrics`.
- **Grafana:** Visualizes metrics through pre-configured dashboards.

---

## 🚀 Installation & Setup

### 1. Local Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure Environment
cp .env.example .env
# Edit .env with your GEMINI_API_KEY and SECRET_KEY

# Run Application
python app.py
```
*App will be available at: http://localhost:5000*

### 2. Docker Execution
```bash
# Build and run with Docker Compose
docker compose up --build -d
```
- **ShieldOps App:** http://localhost:5000
- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3000
- **Metrics Endpoint:** http://localhost:5000/metrics

### 3. Production Deployment (Render)
The project is optimized for deployment on **Render** via Docker:
- **Automatic Initialization:** `init_db.py` handles database setup before the web server starts.
- **Gunicorn:** Production-grade WSGI server with single-worker configuration for SQLite stability.
- **Dynamic Port Binding:** Automatically respects the `$PORT` environment variable.

---

## 📂 Project Structure
```text
ShieldOps/
├── app.py                # Main Flask Application
├── models.py             # Database Models
├── ai_service.py         # Multi-Provider AI Integration
├── init_db.py            # Database Initialization Script
├── requirements.txt      # Dependency List
├── Dockerfile            # Container Specification
├── docker-compose.yml    # Service Orchestration
├── prometheus.yml        # Monitoring Config
├── zap.conf              # DAST Policy
├── .env.example          # Environment Template
├── static/               # CSS, JS, and Images
├── templates/            # HTML Views
├── tests/                # Unit and Integration Tests
├── docs/                 # Audit and Architecture Documentation
└── .github/workflows/    # CI/CD Configuration
```

## 📸 Screenshots
*[Add screenshots here: Dashboard, Simulation Results, Comparison View, Grafana Dashboard]*

---

## 🤝 Contributors
- **Kushi Kaveramma K S** (1MS23CS095)
- **Manya Ravishankar** (1MS23CS227)

---
*Developed for the DevOps Project Curriculum.*
