from fastapi import FastAPI, HTTPException, Query
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import List, Optional
from pydantic import BaseModel

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
    seed_data()

def seed_data():
    """Seed the database with initial cargo data if empty."""
    with Session(engine) as session:
        # Check if data already exists
        existing_data = session.exec(select(Cargo)).first()
        if not existing_data:
            sample_products = [
                Cargo(name="Laptop", description="Dell Inspiron 15 with Intel i7 processor",
                      category="Electronics", weight=2.5, volume=0.01, fragile=True),
                Cargo(name="Books", description="10 Science books",
                      category="Education", weight=5.0, volume=0.02, fragile=False)
            ]
            session.add_all(sample_products)
            session.commit()

@app.on_event("startup")
def on_startup():
    init_db()

# Add Cargo
@app.post("/cargo", response_model=Cargo)
def add_cargo(cargo: Cargo):
    """Add a new cargo item to storage."""
    with Session(engine) as session:
        session.add(cargo)
        session.commit()
        session.refresh(cargo)
    return cargo

# Get Cargo by ID
@app.get("/cargo/{cargo_id}", response_model=Cargo)
def get_cargo(cargo_id: int):
    """Retrieve a specific cargo item by ID."""
    with Session(engine) as session:
        cargo = session.get(Cargo, cargo_id)
        if not cargo:
            raise HTTPException(status_code=404, detail="Cargo not found")
        return cargo

# List all Cargo
@app.get("/cargo", response_model=List[Cargo])
def list_cargo():
    """List all stored cargo items."""
    with Session(engine) as session:
        return session.exec(select(Cargo)).all()

# Update Cargo (Supports Partial Updates)
@app.put("/cargo/{cargo_id}", response_model=Cargo)
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

# Delete Cargo
@app.delete("/cargo/{cargo_id}", response_model=dict)
def delete_cargo(cargo_id: int):
    """Delete a cargo item from storage."""
    with Session(engine) as session:
        cargo = session.get(Cargo, cargo_id)
        if not cargo:
            raise HTTPException(status_code=404, detail="Cargo not found")
        session.delete(cargo)
        session.commit()
    return {"message": "Cargo deleted successfully"}

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

    return {
        "optimized_cargo": [{"id": c.id, "name": c.name, "weight": c.weight, "volume": c.volume} for c in optimized_cargo],
        "total_weight": total_weight,
        "total_volume": total_volume
    }

# Run the FastAPI App
from typing import List, Dict, Any

def format_response(optimized_cargo: List[Any], total_weight: float, total_volume: float) -> Dict[str, Any]:
    return {
        "optimized_cargo": [{"id": c.id, "name": c.name, "weight": c.weight, "volume": c.volume} for c in optimized_cargo],
        "total_weight": total_weight,
        "total_volume": total_volume
    }

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

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