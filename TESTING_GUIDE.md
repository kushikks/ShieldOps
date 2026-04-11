# 🧪 ShieldOps Testing Guide

## ✅ Application is Running!

**URL:** http://localhost:5000

---

## 🎯 How to Test the Enhanced Context Detection

### Test 1: Gas Leak Scenario

1. **Fill in the form:**
   - Disaster Type: **Flood**
   - Severity: **7**
   - Population: **50,000**
   - Medical Resources:
     - Hospital Status: **Moderate**
     - Doctor Availability: **Moderate**
   - Water & Food:
     - Water Supply: **Moderate**
     - Food Supply: **Moderate**
   - Logistics:
     - Transport Status: **Moderate**
     - Communication Status: **Moderate**
   - Emergency Response:
     - Personnel: **Moderate**
     - Equipment: **Moderate**
   - Infrastructure: **Moderately Damaged (50)**
   - **Additional Context:** `Gas leak detected in residential area`

2. **Click "Run Simulation"**

3. **Expected Results:**
   - Risk Score: **~57-60** (increased by +15 points due to gas leak)
   - Priority: **MEDIUM or HIGH**
   - Recommendation includes: **"CRITICAL HAZMAT EMERGENCY: Immediate evacuation..."**

---

### Test 2: Building Collapse

1. **Use same settings as above, but change:**
   - **Additional Context:** `Building collapsed, people trapped inside`

2. **Expected Results:**
   - Risk Score: **~52-55** (increased by +10 points)
   - Recommendation includes: **"STRUCTURAL COLLAPSE: Deploy urban search and rescue teams..."**

---

### Test 3: Fire Spreading

1. **Change disaster type and context:**
   - Disaster Type: **Fire**
   - **Additional Context:** `Fire spreading out of control, wind picking up`

2. **Expected Results:**
   - Risk Score: **Increased by +10 points**
   - Recommendation includes: **"FIRE EMERGENCY: Deploy additional fire brigades..."**

---

### Test 4: Multiple Issues

1. **Test compound scenarios:**
   - **Additional Context:** `Gas leak and building damage, roads blocked`

2. **Expected Results:**
   - Risk Score: **Increased by +15 points** (gas leak is highest priority)
   - Multiple specific recommendations

---

### Test 5: Positive Development

1. **Test risk reduction:**
   - **Additional Context:** `Emergency supplies arrived, situation stabilizing`

2. **Expected Results:**
   - Risk Score: **Decreased by -5 points**
   - Recommendation includes: **"SITUATION UPDATE: Continue monitoring..."**

---

## 🔄 Testing Re-evaluation

1. **Run initial simulation** with context: `Gas leak detected`
2. **Click "Update Assessment"**
3. **Change context to:** `Gas leak contained, area secured`
4. **Click "Re-evaluate Risk"**
5. **Expected:** Risk should decrease, recommendations should change

---

## 📊 Context Scenarios to Test

### Critical Hazmat (+15 points):
- `Gas leak detected`
- `Chemical spill reported`
- `Toxic fumes spreading`
- `Hazardous materials exposure`

### High Impact (+10-12 points):
- `Explosion at factory`
- `Fire spreading rapidly`
- `Building collapsed`
- `Many casualties reported`

### Medium-High (+7-9 points):
- `Disease outbreak`
- `Water rising rapidly`
- `Evacuation routes blocked`
- `People trapped, cannot evacuate`

### Medium (+5-6 points):
- `Power outage across city`
- `Roads blocked by debris`
- `Aftershocks continuing`
- `Looting reported`

### Positive (-5 points):
- `Supplies arrived`
- `Roads cleared`
- `Situation stabilizing`
- `Medical team deployed`

---

## 🎨 What to Look For

### 1. Risk Score Changes:
- Without context: **~42 points**
- With "Gas leak": **~57 points** (+15)
- With "Building collapse": **~52 points** (+10)
- With "Supplies arrived": **~37 points** (-5)

### 2. Reasoning Section:
Should show:
```
→ Additional context INCREASES risk by 15.0 points:
  - Hazardous material/gas leak detected - immediate evacuation required
```

### 3. Recommendations:
Should include specific actions like:
```
CRITICAL HAZMAT EMERGENCY: Immediate evacuation of affected area. 
Deploy hazmat teams with protective equipment. Establish exclusion zone...
```

### 4. Priority Changes:
- Context can push risk from MEDIUM → HIGH
- Or reduce from HIGH → MEDIUM

---

## 🧪 Quick Test Commands (PowerShell)

### Test Gas Leak via API:
```powershell
$body = @{
    disaster_type = "flood"
    severity = 7
    population = 50000
    medical_resources = @{
        hospital_status = "moderate"
        doctor_availability = "moderate"
    }
    water_food_resources = @{
        water_supply = "moderate"
        food_supply = "moderate"
    }
    logistics_resources = @{
        transport_status = "moderate"
        communication_status = "moderate"
    }
    emergency_resources = @{
        personnel_availability = "moderate"
        equipment_status = "moderate"
    }
    infrastructure_quality = 50
    additional_context = "Gas leak detected"
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:5000/api/simulate" -Method Post -Body $body -ContentType "application/json"
```

---

## 🎯 Success Criteria

✅ **Context Detection:**
- Gas leak adds +15 points
- Building collapse adds +10 points
- Fire spreading adds +10 points

✅ **Specific Recommendations:**
- Each scenario gets unique action plan
- Recommendations are detailed and actionable
- Emergency protocols are appropriate

✅ **Re-evaluation:**
- Context changes affect risk in re-evaluation
- Can update context and see immediate impact
- Unlimited re-evaluations work

✅ **UI Display:**
- Risk score updates correctly
- Reasoning shows context impact
- Recommendations display properly

---

## 🐛 Troubleshooting

### If localhost:5000 doesn't load:
```bash
# Check if Flask is running
curl http://localhost:5000/health

# Restart Flask
wsl bash -c "cd ShieldOps && fuser -k 5000/tcp"
wsl bash -c "cd ShieldOps && source venv/bin/activate && python app.py"
```

### If context doesn't affect risk:
- Check browser console for errors
- Verify "Additional Context" field has text
- Try refreshing the page
- Check that you clicked "Run Simulation" or "Re-evaluate Risk"

---

## 📝 Example Test Session

1. **Open:** http://localhost:5000
2. **Select:** Flood, Severity 7, Population 50,000
3. **Set all resources to:** Moderate
4. **Infrastructure:** Moderately Damaged
5. **Context:** Leave empty
6. **Run Simulation** → Note risk score (e.g., 42)
7. **Click "Update Assessment"**
8. **Add context:** "Gas leak detected"
9. **Re-evaluate Risk** → Risk should increase to ~57
10. **Change context:** "Gas leak contained"
11. **Re-evaluate Risk** → Risk should decrease

---

## 🎉 Expected Behavior

The system should now:
- ✅ Detect 15+ critical scenarios from natural language
- ✅ Apply appropriate risk adjustments (+5 to +15 points)
- ✅ Generate specific, actionable recommendations
- ✅ Work in both initial simulation and re-evaluation
- ✅ Show detailed reasoning for risk changes
- ✅ Display professional emergency response protocols

---

**Happy Testing! 🚀**

If you encounter any issues, check the Flask terminal output for errors.

