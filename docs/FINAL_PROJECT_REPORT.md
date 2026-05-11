# FINAL PROJECT REPORT
## DevOps-Enabled Disaster Response Simulation and Decision Intelligence System

**Team:** ShieldOps  
**Members:**  
- Kushi Kaveramma K S (1MS23CS095)  
- Manya Ravishankar (1MS23CS227)  

**Date:** May 2026  

---

### 1. Abstract
The ShieldOps project is an integrated decision intelligence platform designed to enhance disaster response coordination. By combining a Flask-based simulation engine with AI-driven recommendations and a robust DevOps infrastructure, the system provides a secure, scalable, and verifiable environment for emergency planning. The project emphasizes the "Shift Left" security philosophy, integrating automated quality gates into the development lifecycle.

### 2. Problem Statement
Disaster response often suffers from information overload and fragmented resource tracking. Traditional systems lack the agility to update situational assessments dynamically or the security rigor required for critical infrastructure tools. ShieldOps addresses this by providing a unified simulation framework that calculates risk in real-time and suggests prioritized interventions while maintaining a 100% automated security and stability pipeline.

### 3. Objectives
- **Application:** Develop a user-friendly interface for disaster simulation, history tracking, and situation comparison.
- **DevOps:** Implement a fully automated CI/CD pipeline to ensure high availability and rapid iteration.
- **Security:** Integrate SAST, SCA, and DAST to maintain a vulnerability-free codebase.
- **Monitoring:** Provide real-time visibility into application performance and health via Prometheus and Grafana.

### 4. Selected Tools and Their Roles
| Tool | Role | Rationale |
| :--- | :--- | :--- |
| **Flask** | Backend Framework | Lightweight, Pythonic, and easy to integrate with AI libraries. |
| **SQLite / SQLAlchemy**| Database | Simplified persistence for simulation history and user data. |
| **Docker** | Containerization | Ensures environment parity between development and production. |
| **Docker Compose** | Orchestration | Simplifies the management of the App + Monitoring stack. |
| **GitHub Actions** | CI/CD | Native integration with the repository for automated quality gates. |
| **Pytest** | Testing | Robust framework for unit and API validation. |
| **Semgrep** | SAST | High-speed static analysis for security and code quality. |
| **Safety** | SCA | Specifically targets vulnerabilities in the Python dependency tree. |
| **Trivy** | FS/Image Scan | Comprehensive scanning for filesystem and OS-level vulnerabilities. |
| **OWASP ZAP** | DAST | Industry standard for dynamic security testing and header validation. |
| **Prometheus** | Monitoring | Time-series metrics collection via the `/metrics` endpoint. |
| **Grafana** | Visualization | Dashboarding for real-time monitoring of application health. |

### 5. System Architecture
The ShieldOps architecture is divided into four main layers:

1.  **Presentation Layer:** Responsive HTML/JS frontend using Leaflet for geospatial visualization.
2.  **Intelligence Layer:** A Python-based simulation engine that calculates weighted risk scores and interfaces with the Google Gemini and OpenRouter APIs for resilient recommendations.
3.  **Persistence Layer:** SQLite database managed by SQLAlchemy for simulation history and learning records.
4.  **DevOps Layer:** Containerized services orchestrated by Docker Compose (local) or Render (production), monitored by Prometheus.

#### Text-Based Diagram:
[ User Browser ] <--> [ Flask App (Gunicorn) ] <--> [ SQLite DB ]
                            |             |
                            |             +--> [ Gemini / OpenRouter API ]
                            |
                    [ Prometheus ] <--> [ Grafana Dashboard ]
```

### 6. CI/CD Pipeline Architecture
The GitHub Actions workflow (`ci.yml`) executes the following stages sequentially:

- **Checkout:** Retrieves the latest code.
- **Python Setup:** Configures the environment and installs dependencies.
- **Unit Testing:** Runs 65+ test cases via `pytest` with coverage reporting.
- **SAST (Semgrep):** Scans for insecure code patterns.
- **SCA (Safety):** Audits `requirements.txt` for vulnerable packages.
- **FS Scan (Trivy):** Analyzes the project filesystem for exposed secrets or risks.
- **DAST (ZAP):** Performs a dynamic scan of the running container to verify security headers and XSS protection.
- **Artifact Upload:** Saves security reports and test logs for audit purposes.

### 7. Implementation Details
- **Risk Score Calculation:** Uses a weighted formula: `(Severity * Population) / (Resources * Infrastructure)`. Contextual inputs (e.g., "Roads blocked") apply dynamic modifiers to the final score.
- **AI Recommendation Engine:** Implements a resilient multi-provider fallback system. The system attempts generation via **Google Gemini** (with internal model rotation), falling back to **OpenRouter** (Llama 3.1) and finally local **Ollama** or rule-based logic to ensure 100% availability.
- **Simulation Comparison:** The re-evaluation feature allows users to load a past simulation, update resource parameters, and see the delta in risk and priority.
- **Monitoring:** Custom Prometheus metrics track `http_requests_total` and `app_request_latency_seconds`.

### 8. Challenges and Solutions
- **Challenge:** OWASP ZAP failing due to `require-corp` header.
  - **Solution:** Relaxed COEP headers to allow external map tiles while maintaining CSP.
- **Challenge:** Safety scan EOF errors in CI.
  - **Solution:** Downgraded to Safety 2.4.0 to avoid mandatory interactive login prompts.
- **Challenge:** Gemini API 429/403 errors (Quota/Permission).
  - **Solution:** Implemented a provider-level fallback mechanism that automatically switches to OpenRouter when Gemini limits are reached.

### 9. Results and Validation
- **Stability:** 100% test pass rate.
- **Security:** Clean reports from Semgrep, Safety, and Trivy.
- **Visibility:** Real-time metrics available in Prometheus.
- **Scalability:** Docker-ready and successfully deployed to **Render** at [shieldops-eiqm.onrender.com](https://shieldops-eiqm.onrender.com/).

### 10. Future Enhancements
- **Real-Time Data:** Integration with USGS or weather APIs for live disaster feeds.
- **RBAC:** Implementation of Role-Based Access Control for different responder levels.
- **Advanced Monitoring:** Automated alerting via Slack/Discord for system failures.

---
**Report generated by ShieldOps DevOps Team.**
