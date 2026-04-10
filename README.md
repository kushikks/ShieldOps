# 🛡️ ShieldOps - Disaster Response Intelligence System

A comprehensive **Disaster Response Simulation & Decision Intelligence Dashboard** with a complete **DevSecOps CI/CD pipeline**.

## 📋 Project Overview

ShieldOps is a decision-support system that simulates disaster scenarios and provides:
- **Risk Assessment**: Calculates risk scores based on severity and population impact
- **Priority Classification**: Categorizes disasters as LOW, MEDIUM, or HIGH priority
- **Action Recommendations**: Provides specific response strategies for each disaster type
- **Visual Dashboard**: Interactive web interface with real-time insights
- **Automated Pipeline**: Complete CI/CD with security scanning and testing

## 🏗️ Architecture

### Application Stack
- **Backend**: Python Flask REST API
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Containerization**: Docker
- **Testing**: Pytest with coverage
- **CI/CD**: GitHub Actions

### System Flow
```
User Input → API Processing → Risk Calculation → Priority Determination → Response Generation
```

## 🚀 Features

### Core Functionality
- ✅ 8 Disaster Types (Flood, Earthquake, Fire, Cyclone, Tsunami, Landslide, Drought, Epidemic)
- ✅ Deterministic Risk Calculation
- ✅ Real-time Health Monitoring
- ✅ Simulation History Tracking
- ✅ Input Validation & Error Handling

### Dashboard Features
- 🎨 Modern, Responsive UI
- 📊 Visual Risk Gauge
- 🎯 Priority Badges with Color Coding
- 📈 Risk Meter Visualization
- 📜 Simulation History Display
- 🟢 Live System Status Indicator

## 🔧 Local Development

### Prerequisites
- Python 3.11
- pip
- Virtual environment

### Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/kushikks/ShieldOps.git
cd ShieldOps
```

2. **Create virtual environment**
```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python app.py
```

5. **Access the dashboard**
```
http://localhost:5000
```

### Running Tests
```bash
# Run all tests
pytest test_app.py -v

# Run with coverage
pytest test_app.py --cov=app --cov-report=html
```

## 🐳 Docker Deployment

### Build Image
```bash
docker build -t shieldops:latest .
```

### Run Container
```bash
docker run -d -p 5000:5000 --name shieldops-app shieldops:latest
```

### Health Check
```bash
curl http://localhost:5000/health
```

## 📡 API Endpoints

### Health Check
```http
GET /health
```
Returns system health status

### Simulate Disaster
```http
POST /api/simulate
Content-Type: application/json

{
  "disaster_type": "flood",
  "severity": 7,
  "population": 50000
}
```

**Response:**
```json
{
  "disaster_type": "flood",
  "severity": 7,
  "population": 50000,
  "risk_score": 80.5,
  "priority": "HIGH",
  "recommendation": "Deploy rescue boats, establish evacuation centers...",
  "timestamp": "2024-01-15T10:30:00"
}
```

### Get History
```http
GET /api/history
```
Returns simulation history

### Get Disaster Types
```http
GET /api/disasters
```
Returns available disaster types

## 🔐 DevSecOps Pipeline

### Pipeline Stages

1. **Build Stage**
   - Docker image creation
   - Artifact generation

2. **Test Stage**
   - Unit tests (19 test cases)
   - Coverage analysis
   - Validation testing

3. **Deploy Stage**
   - Container deployment
   - Status verification

4. **Health Check Stage**
   - Endpoint validation
   - Response verification

5. **Functional Testing Stage**
   - API endpoint testing
   - All disaster types validation
   - Input validation testing
   - History tracking verification

6. **Security Scanning Stage**
   - SAST (Semgrep)
   - Dependency scanning (Safety)
   - Container scanning (Trivy)

7. **DAST Stage**
   - Placeholder for dynamic testing
   - Ready for OWASP ZAP integration

8. **Pipeline Summary**
   - Artifact collection
   - Status reporting

### Pipeline Triggers
- Push to `main` or `develop` branches
- Pull requests to `main`

### Artifacts Generated
- Docker images
- Test coverage reports
- Security scan reports
- Pipeline logs

## 🧪 Testing Strategy

### Test Coverage
- ✅ Health check validation
- ✅ Risk calculation logic
- ✅ All disaster type simulations
- ✅ Input validation (positive & negative cases)
- ✅ Edge cases and boundary conditions
- ✅ Deterministic behavior verification
- ✅ History tracking
- ✅ API endpoint functionality

### Test Categories
1. **Functional Tests**: Core feature validation
2. **Scenario Tests**: Different disaster simulations
3. **Failure Tests**: Error handling and validation
4. **Edge Case Tests**: Boundary conditions

## 📊 Risk Calculation Logic

### Formula
```
risk_score = (severity × 10) + (population_factor × 0.5)
```

### Population Factors
- < 1,000: Factor 10
- 1,000 - 10,000: Factor 30
- 10,000 - 100,000: Factor 60
- > 100,000: Factor 90

### Priority Levels
- **HIGH**: Risk Score ≥ 70
- **MEDIUM**: Risk Score 40-69
- **LOW**: Risk Score < 40

## 🎯 Project Goals Achieved

✅ **Runnable Application**: Fully functional web dashboard
✅ **Structured System**: Clear input → processing → output flow
✅ **Container-Ready**: Dockerized with health checks
✅ **Complete CI/CD**: 8-stage automated pipeline
✅ **Comprehensive Testing**: 19 test cases with 100% pass rate
✅ **Security Integration**: SAST, dependency, and container scanning
✅ **DevSecOps Principles**: Security integrated throughout pipeline
✅ **Deterministic Logic**: Consistent, testable outputs
✅ **Professional Quality**: Production-ready code structure

## 📁 Project Structure

```
ShieldOps/
├── .github/
│   └── workflows/
│       └── ci.yml              # CI/CD pipeline
├── static/
│   ├── css/
│   │   └── style.css           # Dashboard styles
│   └── js/
│       └── app.js              # Frontend logic
├── templates/
│   └── index.html              # Dashboard HTML
├── app.py                      # Flask application
├── test_app.py                 # Test suite
├── Dockerfile                  # Container definition
├── requirements.txt            # Python dependencies
├── .dockerignore              # Docker ignore rules
└── README.md                   # Documentation
```

## 🔒 Security Features

- Input validation and sanitization
- Error handling without information leakage
- CORS configuration
- Health check endpoints
- Automated security scanning
- Dependency vulnerability checks
- Container security scanning

## 🚦 Pipeline Status

The pipeline ensures:
- ✅ Code builds successfully
- ✅ All tests pass
- ✅ Application deploys correctly
- ✅ Health checks succeed
- ✅ Functional tests validate behavior
- ✅ Security scans complete
- ✅ Artifacts are generated

## 📈 Future Enhancements

- [ ] Machine Learning integration for better predictions
- [ ] Real-time data integration
- [ ] Multi-language support
- [ ] Advanced visualization (charts, maps)
- [ ] User authentication
- [ ] Database persistence
- [ ] OWASP ZAP DAST implementation
- [ ] Performance testing
- [ ] Load testing

## 👥 Contributors

- **Kushi** - DevOps & CI/CD Implementation

## 📄 License

This project is created for educational purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📞 Support

For issues or questions, please open an issue on GitHub.

---

**Built with ❤️ using DevSecOps principles**
