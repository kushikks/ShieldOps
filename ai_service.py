"""
AI Service for generating dynamic disaster response recommendations
Supports both Google Gemini API and local Ollama models
"""

import os
import json
from typing import Dict, List, Optional
import requests


class AIRecommendationService:
    """Service for generating AI-powered disaster response recommendations"""
    
    def __init__(self):
        self.use_local_ai = os.getenv('USE_LOCAL_AI', 'false').lower() == 'true'
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'llama2')
        
        # Debug logging
        print(f"[AI Service] Initializing...")
        print(f"[AI Service] USE_LOCAL_AI: {self.use_local_ai}")
        print(f"[AI Service] GEMINI_API_KEY present: {bool(self.gemini_api_key)}")
        if self.gemini_api_key:
            print(f"[AI Service] GEMINI_API_KEY length: {len(self.gemini_api_key)}")
        
        # Initialize Gemini client if using cloud AI
        if not self.use_local_ai and self.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
                
                # List available models to find the right ones
                print("[AI Service] Checking available models...")
                self.available_gemini_models = []
                try:
                    for model in genai.list_models():
                        if 'generateContent' in model.supported_generation_methods:
                            self.available_gemini_models.append(model.name)
                            print(f"[AI Service]   - {model.name}")
                    
                    if not self.available_gemini_models:
                        print("[AI Service] ✗ No models support generateContent")
                        self.gemini_model = None
                        return

                    # Define preference order
                    self.preferred_models = [
                        'models/gemini-1.5-flash',
                        'models/gemini-2.0-flash',
                        'models/gemini-1.5-pro',
                        'models/gemini-pro'
                    ]
                    
                    # Find the first preferred model that is actually available
                    self.current_model_index = -1
                    for i, preferred in enumerate(self.preferred_models):
                        if preferred in self.available_gemini_models:
                            self.current_model_name = preferred
                            self.current_model_index = i
                            break
                    
                    if self.current_model_index == -1:
                        self.current_model_name = self.available_gemini_models[0]
                    
                    print(f"[AI Service] Selected primary model: {self.current_model_name}")
                    self.gemini_model = genai.GenerativeModel(self.current_model_name)
                    print("[AI Service] ✓ Gemini model initialized successfully")
                    
                except Exception as e:
                    print(f"[AI Service] ✗ Error listing models: {e}")
                    self.gemini_model = None
            except ImportError as e:
                print(f"[AI Service] ✗ Import error: {e}")
                print("Warning: google-generativeai package not installed. Install with: pip install google-generativeai")
                self.gemini_model = None
            except Exception as e:
                print(f"[AI Service] ✗ Gemini initialization error: {e}")
                self.gemini_model = None
        else:
            self.gemini_model = None
            if self.use_local_ai:
                print("[AI Service] Using local AI (Ollama)")
            else:
                print("[AI Service] ✗ No GEMINI_API_KEY found - using fallback")
    
    def generate_recommendation(
        self,
        disaster_type: str,
        severity: int,
        population: int,
        risk_score: float,
        priority: str,
        lat: float = None,
        lng: float = None,
        medical_resources: Optional[Dict] = None,
        water_food_resources: Optional[Dict] = None,
        logistics_resources: Optional[Dict] = None,
        emergency_resources: Optional[Dict] = None,
        infrastructure_quality: int = 50,
        additional_context: str = ""
    ) -> str:
        """
        Generate AI-powered recommendations based on disaster scenario
        
        Returns:
            str: AI-generated recommendation text
        """
        
        # Build comprehensive prompt
        prompt = self._build_prompt(
            disaster_type, severity, population, risk_score, priority,
            lat, lng,
            medical_resources, water_food_resources, logistics_resources,
            emergency_resources, infrastructure_quality, additional_context
        )
        
        # Check if we are in testing mode to return deterministic results
        try:
            from flask import current_app
            if current_app and current_app.config.get('TESTING'):
                print("[AI Service] TESTING mode detected - using fallback")
                return self._generate_fallback(disaster_type, priority, additional_context)
        except Exception:
            pass
            
        # Try AI generation
        try:
            if self.use_local_ai:
                print("[AI Service] Attempting Ollama generation...")
                return self._generate_with_ollama(prompt)
            elif self.gemini_model:
                print("[AI Service] Attempting Gemini generation...")
                return self._generate_with_gemini(prompt)
            else:
                print("[AI Service] No AI available - using fallback")
                return self._generate_fallback(disaster_type, priority, additional_context)
        except Exception as e:
            print(f"[AI Service] AI generation failed: {type(e).__name__}: {e}")
            print("[AI Service] Falling back to rule-based recommendations")
            return self._generate_fallback(disaster_type, priority, additional_context)
    
    def _build_prompt(
        self,
        disaster_type: str,
        severity: int,
        population: int,
        risk_score: float,
        priority: str,
        lat: float,
        lng: float,
        medical_resources: Optional[Dict],
        water_food_resources: Optional[Dict],
        logistics_resources: Optional[Dict],
        emergency_resources: Optional[Dict],
        infrastructure_quality: int,
        additional_context: str
    ) -> str:
        """Build comprehensive prompt for AI model"""
        
        prompt = f"""Generate disaster response recommendations for this emergency situation.

SCENARIO:
• Disaster: {disaster_type.upper()}
• Severity: {severity}/10
• Population: {population:,}
• Location Coordinates: Latitude {lat}, Longitude {lng}
• Risk Score: {risk_score:.1f}/100
• Priority: {priority}

CURRENT RESOURCES:"""

        critical_issues = []
        
        if medical_resources:
            hospital = medical_resources.get('hospital_status', 'unknown')
            doctors = medical_resources.get('doctor_availability', 'unknown')
            prompt += f"""
• Hospital Status: {hospital.upper()}
• Doctor Availability: {doctors.upper()}"""
            if hospital in ['critical', 'collapsed']:
                critical_issues.append(f"Hospital {hospital}")
            if doctors in ['scarce', 'none']:
                critical_issues.append(f"Doctors {doctors}")

        if water_food_resources:
            water = water_food_resources.get('water_supply', 'unknown')
            food = water_food_resources.get('food_supply', 'unknown')
            prompt += f"""
• Water Supply: {water.upper()}
• Food Supply: {food.upper()}"""
            if water in ['critical', 'none']:
                critical_issues.append(f"Water {water}")
            if food in ['scarce', 'none']:
                critical_issues.append(f"Food {food}")

        if logistics_resources:
            transport = logistics_resources.get('transport_status', 'unknown')
            comm = logistics_resources.get('communication_status', 'unknown')
            prompt += f"""
• Transport: {transport.upper()}
• Communication: {comm.upper()}"""
            if transport in ['limited', 'collapsed']:
                critical_issues.append(f"Transport {transport}")
            if comm in ['limited', 'collapsed']:
                critical_issues.append(f"Communication {comm}")

        if emergency_resources:
            personnel = emergency_resources.get('personnel_availability', 'unknown')
            equipment = emergency_resources.get('equipment_status', 'unknown')
            prompt += f"""
• Personnel: {personnel.upper()}
• Equipment: {equipment.upper()}"""
            if personnel in ['limited', 'none']:
                critical_issues.append(f"Personnel {personnel}")
            if equipment in ['limited', 'none']:
                critical_issues.append(f"Equipment {equipment}")

        prompt += f"""
• Infrastructure: {infrastructure_quality}%"""

        if additional_context:
            prompt += f"""

ADDITIONAL CONTEXT:
{additional_context}"""
            critical_issues.append("Additional context situation")

        if critical_issues:
            prompt += f"""

CRITICAL ISSUES TO ADDRESS:
{chr(10).join(f"• {issue}" for issue in critical_issues)}"""

        prompt += """

GENERATE RESPONSE IN THIS EXACT FORMAT (use plain text, NO markdown asterisks):

CRITICAL ACTIONS (Prioritized by urgency):

• [Action 1 - Most critical shortage with specific numbers and comprehensive solution]

• [Action 2 - Second critical shortage with specific numbers and comprehensive solution]

• [Action 3 - Third critical shortage with specific numbers and comprehensive solution]

• [Action 4 - Fourth critical shortage with specific numbers and comprehensive solution]

• [Action 5 - Fifth critical shortage with specific numbers and comprehensive solution]

• [Action 6 - Sixth critical action covering remaining issues with specific numbers]


EMERGENCY CONTACTS & RESOURCES:

Based on the location coordinates provided (Latitude {lat}, Longitude {lng}), provide the CORRECT local emergency contacts for that specific country and region:

• National Emergency number for that country | Police | Fire | Ambulance

• National Disaster Management agency name and contact for that country

• Nearest Red Cross / Red Crescent branch contact for that country

• WHO Regional Office contact relevant to that country


NEXT STEPS (Timeline):

• 0-30 min: [Immediate first action]

• 30-120 min: [Critical follow-up action]

• 2-6 hours: [Short-term priority]

• 6-24 hours: [Sustained operations setup]

• 24+ hours: [Recovery phase initiation]


CRITICAL REQUIREMENTS:
- DO NOT use markdown asterisks (** or *) anywhere
- Add TWO blank lines between major sections
- Add ONE blank line after each bullet point
- MUST have EXACTLY 5-6 action points (no more, no less)
- Each action point must be COMPREHENSIVE - combine multiple related issues
- Each action must include specific numbers, quantities, and deployment details
- Address ALL critical resource shortages across the 5-6 points
- MUST include Emergency Contacts section with the CORRECT numbers for the country determined from the coordinates
- MUST include Next Steps section with 5 timeline points
- Total response: 500-700 words
- Start directly with "CRITICAL ACTIONS (Prioritized by urgency):"
- Ensure response is COMPLETE - all sections must be present
- Make each point detailed enough to cover multiple aspects
"""

        return prompt
    
    def _generate_with_gemini(self, prompt: str) -> str:
        """Generate recommendation using Google Gemini API with automatic model rotation for 403 errors"""
        import google.generativeai as genai
        
        try:
            print(f"[AI Service] Calling Gemini API with model {self.current_model_name}...")
            response = self.gemini_model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'max_output_tokens': 4096,
                    'top_p': 0.95,
                }
            )
            
            print("[AI Service] ✓ Gemini API call successful")
            return response.text.strip()
        
        except Exception as e:
            # If 403 Permission Denied, try the next available model in the preference list
            if "403" in str(e) or "PermissionDenied" in type(e).__name__:
                print(f"[AI Service] ✗ Gemini 403 Error with {self.current_model_name}")
                
                # Try to find the next model to use
                next_index = self.current_model_index + 1
                while next_index < len(self.preferred_models):
                    next_model = self.preferred_models[next_index]
                    if next_model in self.available_gemini_models:
                        print(f"[AI Service] ↺ Rotating to next model: {next_model}")
                        self.current_model_name = next_model
                        self.current_model_index = next_index
                        self.gemini_model = genai.GenerativeModel(self.current_model_name)
                        # Recursive call to try with the new model
                        return self._generate_with_gemini(prompt)
                    next_index += 1
                
                # If we've exhausted preferred models, try any remaining available models
                for model in self.available_gemini_models:
                    if model not in self.preferred_models:
                        print(f"[AI Service] ↺ Trying alternative available model: {model}")
                        self.current_model_name = model
                        self.gemini_model = genai.GenerativeModel(self.current_model_name)
                        # Prevent infinite loop by removing it from available list
                        self.available_gemini_models.remove(model)
                        return self._generate_with_gemini(prompt)

            print(f"[AI Service] ✗ Gemini API error: {type(e).__name__}: {e}")
            raise
    
    def _generate_with_ollama(self, prompt: str) -> str:
        """Generate recommendation using local Ollama model"""
        try:
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 500
                    }
                },
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            return result.get('response', '').strip()
        
        except Exception as e:
            print(f"Ollama API error: {e}")
            raise
    
    def _generate_fallback(self, disaster_type: str, priority: str, additional_context: str) -> str:
        """Fallback to rule-based recommendations when AI is unavailable"""
        
        base_actions = {
            'flood': 'Deploy rescue boats and establish evacuation centers. Distribute clean water and set up temporary shelters. Monitor water levels and secure hazardous materials.',
            'earthquake': 'Deploy search and rescue teams immediately. Set up medical triage centers. Assess structural damage and evacuate unsafe buildings. Establish communication networks.',
            'fire': 'Deploy fire brigades and evacuate affected areas. Establish air quality monitoring. Set up emergency shelters and medical stations for smoke inhalation treatment.',
            'cyclone': 'Activate early warning systems and establish emergency shelters. Secure critical infrastructure. Deploy emergency response teams to affected areas.',
            'tsunami': 'Immediate evacuation to high ground. Activate coastal warning systems. Deploy rescue teams and establish safe zones. Monitor for aftershocks.',
            'landslide': 'Deploy rescue teams and establish safe zones. Monitor geological activity. Evacuate at-risk areas and assess slope stability.',
            'drought': 'Distribute emergency water supplies. Implement water conservation measures. Provide agricultural support and food assistance.',
            'epidemic': 'Deploy medical teams with protective equipment. Establish quarantine zones and isolation facilities. Implement contact tracing and distribute medical supplies.'
        }
        
        recommendation = base_actions.get(disaster_type, 'Deploy emergency response teams and assess the situation.')
        
        if priority == 'HIGH':
            recommendation += ' URGENT: Request immediate external aid and mobilize all available resources. Establish incident command center.'
        elif priority == 'MEDIUM':
            recommendation += ' Request additional resources from neighboring regions. Coordinate with local authorities.'
        
        if additional_context:
            recommendation += f' NOTE: {additional_context} - Adjust response accordingly.'
        
        recommendation += '\n\n⚠️ AI recommendations unavailable. Using fallback system. Configure GEMINI_API_KEY or USE_LOCAL_AI for enhanced recommendations.'
        
        return recommendation


# Global service instance
_ai_service = None


def get_ai_service() -> AIRecommendationService:
    """Get or create AI service singleton"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIRecommendationService()
    return _ai_service
