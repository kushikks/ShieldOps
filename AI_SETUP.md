# AI-Powered Recommendations Setup

ShieldOps now uses **Google Gemini AI** to generate dynamic, context-aware disaster response recommendations instead of hardcoded solutions.

## Features

- **Dynamic Recommendations**: AI analyzes the complete disaster scenario and generates specific, actionable recommendations
- **Context-Aware**: Considers all resource states, infrastructure quality, and additional context
- **Fallback System**: Automatically falls back to rule-based recommendations if AI is unavailable
- **Local AI Option**: Can use Ollama for completely offline AI recommendations

---

## Setup Options

### Option 1: Google Gemini API (Recommended)

#### Step 1: Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Get API Key"** or **"Create API Key"**
4. Copy your API key

#### Step 2: Configure Environment

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Gemini API key:
   ```bash
   GEMINI_API_KEY=your_actual_api_key_here
   USE_LOCAL_AI=false
   ```

#### Step 3: Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install updated requirements
pip install -r requirements.txt
```

#### Step 4: Run the Application

```bash
python app.py
```

The application will now use Gemini AI for generating recommendations!

---

### Option 2: Local AI with Ollama (No API Key Required)

If you prefer to run AI completely offline without any API keys:

#### Step 1: Install Ollama

- **Linux/Mac**: 
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```

- **Windows**: Download from [ollama.com](https://ollama.com/download)

#### Step 2: Download a Model

```bash
ollama pull llama2
# or
ollama pull mistral
```

#### Step 3: Configure Environment

Edit `.env`:
```bash
USE_LOCAL_AI=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

#### Step 4: Start Ollama (if not running)

```bash
ollama serve
```

#### Step 5: Run the Application

```bash
python app.py
```

---

## How It Works

### AI-Generated Recommendations Include:

1. **Immediate Actions** (0-2 hours)
   - Life-saving priorities
   - Emergency response deployment
   - Critical resource allocation

2. **Short-term Priorities** (2-24 hours)
   - Sustained operations
   - Resource replenishment
   - Infrastructure assessment

3. **Resource-Specific Strategies**
   - Medical: Hospital capacity, personnel deployment
   - Supplies: Water/food distribution plans
   - Logistics: Transportation and communication restoration
   - Emergency: Equipment and personnel coordination

4. **Risk Mitigation**
   - Hazard-specific precautions
   - Secondary disaster prevention
   - Safety protocols

5. **Coordination Requirements**
   - Multi-agency coordination
   - External aid requests
   - Communication protocols

### Example AI Prompt

The AI receives comprehensive context:
```
DISASTER SCENARIO:
- Type: EARTHQUAKE
- Severity: 8/10
- Affected Population: 50,000
- Risk Score: 75.5/100
- Priority Level: HIGH

RESOURCE ASSESSMENT:
Medical Resources:
  - Hospital Status: critical
  - Doctor Availability: limited
Water & Food Supply:
  - Water Supply: moderate
  - Food Supply: adequate
...

ADDITIONAL CONTEXT:
Gas leak detected in downtown area
```

The AI then generates specific, actionable recommendations tailored to this exact scenario.

---

## Fallback System

If AI is unavailable (no API key or connection issues), the system automatically falls back to rule-based recommendations with a warning message:

```
⚠️ AI recommendations unavailable. Using fallback system. 
Configure GEMINI_API_KEY or USE_LOCAL_AI for enhanced recommendations.
```

---

## API Costs

### Google Gemini API
- **Model**: gemini-1.5-flash
- **Cost**: FREE tier available
  - 15 requests per minute
  - 1 million tokens per day
  - 1,500 requests per day
- **Pricing**: Very affordable for production use
- **More info**: [Google AI Pricing](https://ai.google.dev/pricing)

### Ollama (Local)
- **Cost**: FREE (runs on your hardware)
- **Privacy**: Complete data privacy, no external API calls
- **Requirements**: ~8GB RAM for llama2, ~16GB for larger models

---

## Testing AI Recommendations

1. Start the application
2. Run a simulation with various resource states
3. Add additional context like "gas leak" or "hospital collapsed"
4. Observe how AI generates specific recommendations based on the scenario

### Example Test Scenarios:

**Scenario 1: Critical Medical Crisis**
- Disaster: Earthquake
- Hospital Status: collapsed
- Doctor Availability: none
- Additional Context: "Multiple building collapses, trapped victims"

**Scenario 2: Supply Emergency**
- Disaster: Flood
- Water Supply: none
- Food Supply: scarce
- Additional Context: "Roads blocked, no access to affected area"

**Scenario 3: Communication Breakdown**
- Disaster: Cyclone
- Communication Status: collapsed
- Transport Status: limited
- Additional Context: "Power outage, cell towers down"

---

## Troubleshooting

### "AI recommendations unavailable" message

**Cause**: Gemini API key not configured or invalid

**Solution**:
1. Check `.env` file exists and has `GEMINI_API_KEY=your_key`
2. Verify API key is valid at [Google AI Studio](https://makersuite.google.com/app/apikey)
3. Check internet connection
4. Try using local AI instead (see Option 2)

### Ollama connection error

**Cause**: Ollama not running or wrong URL

**Solution**:
1. Start Ollama: `ollama serve`
2. Verify it's running: `curl http://localhost:11434/api/tags`
3. Check `OLLAMA_BASE_URL` in `.env`

### Slow AI responses

**Gemini**: Usually responds in 1-3 seconds. Check internet connection.

**Ollama**: First request may be slow (model loading). Subsequent requests are faster. Consider using a smaller model like `llama2:7b` instead of `llama2:13b`.

---

## Benefits Over Hardcoded Recommendations

### Before (Hardcoded):
```
Deploy rescue boats, establish evacuation centers, 
distribute clean water
```

### After (AI-Generated):
```
IMMEDIATE ACTIONS (0-2 hours):
1. Deploy helicopter rescue teams to isolated areas due to 
   blocked roads
2. Establish emergency medical triage at the community center 
   (hospital collapsed)
3. Deploy water purification units - contaminated water supply 
   detected
4. Set up satellite communication - cell towers down

SHORT-TERM PRIORITIES (2-24 hours):
1. Request medical personnel from neighboring regions 
   (no doctors available)
2. Establish temporary field hospital with surgical capability
3. Coordinate food distribution via aerial drops (roads blocked)
4. Deploy generators for critical facilities

RESOURCE DEPLOYMENT:
- Medical: 3 mobile surgical units, 20 doctors, 50 nurses
- Supplies: 10,000L clean water, 5-day food rations for 50,000
- Equipment: 5 helicopters, 10 boats, satellite phones
...
```

The AI provides **specific, actionable, context-aware recommendations** that adapt to the exact situation!

---

## Security Notes

- **Never commit `.env` file** to version control (already in `.gitignore`)
- **Keep API keys secret** - don't share in logs or screenshots
- **Use environment variables** for production deployment
- **Rotate API keys** periodically for security

---

## Support

For issues or questions:
1. Check this documentation
2. Review error messages in console
3. Test with fallback mode first
4. Verify API key and configuration

Enjoy AI-powered disaster response recommendations! 🚀
