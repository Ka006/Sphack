from fastapi import FastAPI, APIRouter, HTTPException, Query
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI()

# Database setup
DATABASE_URL = "sqlite:///cargo_storage.db"
engine = create_engine(DATABASE_URL, echo=True)

# Cargo Model
class Cargo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None  # Added for more details
    category: Optional[str] = None  # Example: "Electronics", "Furniture", etc.
    weight: float  # In kg
    volume: float  # In cubic meters
    fragile: bool = False  # Is the cargo fragile?

# User Data Model
class UserData(BaseModel):
    name: str
    age: int
    email: str

# Initialize database and seed sample data
def init_db():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # Check if data already exists
        existing_data = session.exec(select(Cargo)).first()
        if not existing_data:
            sample_cargo = [
                Cargo(name="Laptop", description="Dell Inspiron 15", category="Electronics", weight=2.5, volume=0.01, fragile=True),
                Cargo(name="Books", description="10 Science books", category="Education", weight=5.0, volume=0.02, fragile=False)
            ]
            session.add_all(sample_cargo)
            session.commit()
            print("Sample data added to the database.")

@app.on_event("startup")
def on_startup():
    init_db()

# Cargo Router
cargo_router = APIRouter(prefix="/cargo", tags=["Cargo"])

@cargo_router.post("/", response_model=Cargo)
def add_cargo(cargo: Cargo):
    """Add a new cargo item to the database."""
    with Session(engine) as session:
        session.add(cargo)
        session.commit()
        session.refresh(cargo)
    return cargo

@cargo_router.get("/", response_model=List[Cargo])
def list_cargo():
    """List all cargo items."""
    with Session(engine) as session:
        return session.exec(select(Cargo)).all()

@cargo_router.get("/{cargo_id}", response_model=Cargo)
def get_cargo(cargo_id: int):
    """Retrieve a specific cargo item by ID."""
    with Session(engine) as session:
        cargo = session.get(Cargo, cargo_id)
        if not cargo:
            raise HTTPException(status_code=404, detail="Cargo not found")
        return cargo

@cargo_router.put("/{cargo_id}", response_model=Cargo)
def update_cargo(cargo_id: int, updated_cargo: Cargo):
    """Update details of a stored cargo item."""
    with Session(engine) as session:
        cargo = session.get(Cargo, cargo_id)
        if not cargo:
            raise HTTPException(status_code=404, detail="Cargo not found")

        cargo_data = updated_cargo.dict(exclude_unset=True)
        for key, value in cargo_data.items():
            setattr(cargo, key, value)

        session.commit()
        session.refresh(cargo)
    return cargo

@cargo_router.delete("/{cargo_id}", response_model=dict)
def delete_cargo(cargo_id: int):
    """Delete a cargo item from the database."""
    with Session(engine) as session:
        cargo = session.get(Cargo, cargo_id)
        if not cargo:
            raise HTTPException(status_code=404, detail="Cargo not found")
        session.delete(cargo)
        session.commit()
    return {"message": "Cargo deleted successfully"}

# Include the cargo router in the main app
app.include_router(cargo_router)

# Optimize Storage
@app.get("/cargo/optimize")
def optimize_storage(
    max_weight: float = Query(..., description="Maximum weight capacity"),
    max_volume: float = Query(..., description="Maximum volume capacity")
):
    """Optimize storage by selecting cargo that fits within given weight and volume constraints."""
    with Session(engine) as session:
        all_cargo = session.exec(select(Cargo)).all()
        optimized_cargo = []
        total_weight = 0
        total_volume = 0

        for cargo in sorted(all_cargo, key=lambda x: (x.weight, x.volume)):
            if total_weight + cargo.weight <= max_weight and total_volume + cargo.volume <= max_volume:
                optimized_cargo.append(cargo)
                total_weight += cargo.weight
                total_volume += cargo.volume

    return format_response(optimized_cargo, total_weight, total_volume)

# Existing code for optimized cargo
def format_response(optimized_cargo: List[Any], total_weight: float, total_volume: float) -> Dict[str, Any]:
    return {
        "optimized_cargo": [{"id": c.id, "name": c.name, "weight": c.weight, "volume": c.volume} for c in optimized_cargo],
        "total_weight": total_weight,
        "total_volume": total_volume
    }

# Expanded items dictionary
expanded_items_dict = {
    "Food Packet": ["Crew_Quarters", "Storage_Bay"],
    "Oxygen Cylinder": ["Airlock", "Crew_Quarters", "Medical_Bay"],
    "First Aid Kit": ["Medical_Bay", "Crew_Quarters"],
    "Water Bottle": ["Crew_Quarters", "Storage_Bay"],
    "Space Suit": ["Storage_Bay", "Airlock"],
    "Tool Kit": ["Maintenance_Bay", "Storage_Bay"],
    "Radiation Shield": ["Storage_Bay", "Engineering_Bay"],
    "Emergency Beacon": ["Command_Center", "Cockpit"],
    "Battery Pack": ["Power_Bay", "External_Storage"],
    "Solar Panel": ["External_Storage", "Power_Bay"],
    "Navigation Module": ["Cockpit", "Command_Center"],
    "Communication Device": ["Command_Center", "Crew_Quarters"],
    "Research Samples": ["Lab", "Storage_Bay"],
    "Fire Extinguisher": ["Crew_Quarters", "Engineering_Bay"],
    "Thruster Fuel": ["Engine_Bay", "Storage_Bay"],
    "Microgravity Lab Kit": ["Lab", "Crew_Quarters"],
    "Pressure Regulator": ["Airlock", "Engineering_Bay"],
    "Cooling System": ["Engineering_Bay", "Power_Bay"],
    "Waste Management Kit": ["Sanitation_Bay", "Engineering_Bay"],
    "Asteroid Sample Container": ["Lab", "Storage_Bay"],
    "3D Printer": ["Engineering_Bay", "Lab"],
    "Laptop": ["Crew_Quarters", "Command_Center"],
    "Scientific Sensor": ["Lab", "Cockpit"],
    "Medical Scanner": ["Medical_Bay", "Lab"],
    "Vacuum Sealed Tools": ["Storage_Bay", "Maintenance_Bay"],
    "EV Suit Battery": ["Airlock", "Storage_Bay"],
    "Tether Reel": ["External_Storage", "Airlock"],
    "CO2 Scrubber": ["Life_Support", "Engineering_Bay"],
    "Water Purification Unit": ["Life_Support", "Crew_Quarters"],
    "Seed Packets": ["Greenhouse", "Lab"],
    "Lab Microscope": ["Lab", "Medical_Bay"],
    "Protein Bars": ["Crew_Quarters", "Storage_Bay"],
    "Antibiotic Supply": ["Medical_Bay", "Lab"],
    "Gyroscope Module": ["Cockpit", "Engineering_Bay"],
    "Circuit Board": ["Engineering_Bay", "Storage_Bay"],
    "Helmet Visor": ["Storage_Bay", "Crew_Quarters"],
    "Emergency Oxygen Mask": ["Crew_Quarters", "Medical_Bay"],
    "LED Work Light": ["Maintenance_Bay", "Engineering_Bay"],
    "Handheld Spectrometer": ["Lab", "Engineering_Bay"],
}

# Endpoint to retrieve expanded items
@app.get("/expanded-items")
def get_expanded_items():
    """Retrieve the expanded items dictionary."""
    return expanded_items_dict

@app.get("/")
def read_root():
    return {"message": "Welcome to the Cargo Management API"}

# Endpoint to collect user data
@app.post("/submit-data/")
def collect_data(user_data: UserData):
    # Log the received data to the terminal
    print(f"Received data: {user_data}")
    return {"status": "success", "received_data": user_data}

# Run the FastAPI App
if __name__ == "__main__":
    import uvicorn
    import os

    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    port = int(os.getenv("FASTAPI_PORT", 8000))

    try:
        uvicorn.run(app, host=host, port=port)
    except Exception as e:
        print(f"Error starting the server: {e}")