from fastapi import FastAPI, HTTPException, Query
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import List, Optional

app = FastAPI()

# Database setup
DATABASE_URL = "sqlite:///cargo_storage.db"
engine = create_engine(DATABASE_URL, echo=True)

class Cargo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    weight: float  # In kg
    volume: float  # In cubic meters
    fragile: bool = False  # Is the cargo fragile

def init_db():
    SQLModel.metadata.create_all(engine)

@app.on_event("startup")
def on_startup():
    init_db()

@app.post("/cargo", response_model=Cargo)
def add_cargo(cargo: Cargo):
    """Add a new cargo item to storage."""
    with Session(engine) as session:
        print("hi")
        session.add(cargo)
        session.commit()
        session.refresh(cargo)
    return cargo

@app.get("/cargo/{cargo_id}", response_model=Cargo)
def get_cargo(cargo_id: int):
    """Retrieve a specific cargo item by ID."""
    with Session(engine) as session:
        cargo = session.get(Cargo, cargo_id)
        if not cargo:
            raise HTTPException(status_code=404, detail="Cargo not found")
        return cargo

@app.get("/cargo", response_model=List[Cargo])
def list_cargo():
    """List all stored cargo items."""
    with Session(engine) as session:
        return session.exec(select(Cargo)).all()

@app.put("/cargo/{cargo_id}", response_model=Cargo)
def update_cargo(cargo_id: int, updated_cargo: Cargo):
    """Update details of a stored cargo item."""
    with Session(engine) as session:
        cargo = session.get(Cargo, cargo_id)
        if not cargo:
            raise HTTPException(status_code=404, detail="Cargo not found")
        cargo.name = updated_cargo.name
        cargo.weight = updated_cargo.weight
        cargo.volume = updated_cargo.volume
        cargo.fragile = updated_cargo.fragile
        session.commit()
        session.refresh(cargo)
    return cargo

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
        
    return {"optimized_cargo": optimized_cargo, "total_weight": total_weight, "total_volume": total_volume}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
