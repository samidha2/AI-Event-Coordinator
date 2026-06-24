# uvicorn main:app --reload
# http://127.0.0.1:8000/docs
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI(title="AI Event Coordinator API")

# Initialize Gemini Model
model = genai.GenerativeModel('gemini-2.5-flash')

# --- Step 2: Context Understanding Tool ---
# Captures event details like type, budget, and location [cite: 32]
class EventRequirements(BaseModel):
    event_type: str = Field(..., example="AI Workshop")
    budget: float = Field(..., gt=0, example=5000.0)
    location: str = Field(..., example="Mumbai")
    attendee_count: int = Field(..., gt=0, example=100)
    duration_days: int = Field(default=1, example=1)
    preferences: str = Field(default="Professional and educational", example="High-tech vibe")

@app.get("/")
def read_root():
    return {"message": "AI Event Coordinator API is online"}

@app.post("/validate-requirements/")
async def validate_requirements(req: EventRequirements):
    """
    Validates inputs before passing them to the AI engine.
    """
    return {
        "status": "Validated",
        "data": req,
        "message": f"Ready to plan a {req.event_type} for {req.attendee_count} people."
    }

#venue Recommendation tool
class VenueResponse(BaseModel):
    event: str
    recommendations: str
@app.post("/recommend-venues/", response_model=VenueResponse)
async def recommend_venues(req: EventRequirements):
    """
    Step 4: Logic layer using LLM to suggest venues based on constraints.
    """
    prompt = f"""
    Act as a professional Venue Expert. Based on the following requirements:
    - Event Type: {req.event_type}
    - Location: {req.location}
    - Attendee Count: {req.attendee_count}
    - Budget: {req.budget}
    - Preferences: {req.preferences}

    Suggest 3 realistic venue types or specific examples suitable for this capacity and budget. 
    Mention key facilities like audio systems or projectors if relevant[cite: 40].
    Format the output as a clean list.
    """
    
    try:
        response = model.generate_content(prompt)
        return {
            "event": req.event_type,
            "recommendations": response.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#schedule and agenda planning tool
@app.post("/generate-agenda/")
async def generate_agenda(req: EventRequirements):
    """
    Step 5: Creates structured event timelines including sessions and breaks.
    """
    prompt = f"""
    You are an Expert Event Strategist. 
    Create a detailed, chronological agenda for a {req.event_type} in {req.location}.
    - Duration: {req.duration_days} day(s)
    - Attendees: {req.attendee_count}
    - Style: {req.preferences}

    Structure the timeline to include:
    1. Registration and Welcome
    2. Keynote or Main Session
    3. Breaks (Networking/Lunch)
    4. Practical Workshops or Activities
    5. Closing remarks

    Return the agenda as a structured list with timestamps.
    """
    
    try:
        response = model.generate_content(prompt)
        return {
            "event_type": req.event_type,
            "agenda": response.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#budget and logistics optimization tool
class BudgetLogisticsResponse(BaseModel):
    event_type: str
    estimated_total_budget: float
    budget_breakdown: dict
    logistics_recommendations: str

@app.post("/plan-budget-logistics/", response_model=BudgetLogisticsResponse)
async def plan_budget_logistics(req: EventRequirements):
    """
    Step 6: Mathematical engine for costs and AI for resource suggestions.
    """
    # 1. Logic Layer: Basic Mathematical Estimation
    # Assuming average cost per head for catering/basic rentals
    cost_per_head = 25.0  # $25 per person
    estimated_catering = req.attendee_count * cost_per_head
    estimated_venue_buffer = req.budget * 0.4  # Allocating 40% of total budget to venue
    
    # 2. AI Layer: Specific Resource Recommendations
    prompt = f"""
    Act as a Logistics & Procurement Manager for a {req.event_type} with {req.attendee_count} people.
    Budget: ${req.budget}. Location: {req.location}.
    
    Suggest the specific resources needed for this event:
    - Audio/Visual (Projectors, Mics, etc.)
    - Seating style (Theater, Classroom, or Round Table)
    - Staffing needs (Registration desk, tech support)
    
    Keep suggestions within a "moderate" budget context.
    """
    
    try:
        response = model.generate_content(prompt)
        
        breakdown = {
            "catering_estimate": estimated_catering,
            "venue_allocation_target": estimated_venue_buffer,
            "other_logistics": req.budget - (estimated_catering + estimated_venue_buffer)
        }
        
        return {
            "event_type": req.event_type,
            "estimated_total_budget": req.budget,
            "budget_breakdown": breakdown,
            "logistics_recommendations": response.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#Implementing Task & Checklist Automation
class ChecklistResponse(BaseModel):
    event_type: str
    checklist: str

@app.post("/generate-checklist/", response_model=ChecklistResponse)
async def generate_checklist(req: EventRequirements):
    """
    Step 7: Generates a dynamic event preparation checklist.
    """
    prompt = f"""
    Act as an Event Project Coordinator. 
    Create a comprehensive preparation checklist for a {req.event_type} in {req.location} for {req.attendee_count} people.
    
    The checklist should be divided into phases:
    1. Pre-Event (Venue booking, equipment rental)
    2. Event Day (Setup, registration, tech-check)
    3. Post-Event (Feedback collection, teardown)
    
    Ensure tasks are specific to the '{req.preferences}' preference.
    Format the output as a Markdown checklist with clickable-style boxes [ ].
    """
    
    try:
        response = model.generate_content(prompt)
        return {
            "event_type": req.event_type,
            "checklist": response.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
