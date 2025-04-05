from fastapi import FastAPI, HTTPException, Query
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import List, Optional

app = FastAPI()

# Database setup
DATABASE_URL = "sqlite:///cargo_storage.db"
engine = create_engine(DATABASE_URL, echo=True)

# Cargo Model
class Cargo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str  # Define the field as a string

# Initialize the database and seed data
def init_db():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # Check if data already exists
        existing_data = session.query(Cargo).first()
        if not existing_data:
            # Insert "Kamalesh" as a sample data
            sample_cargo = Cargo(name="Kamalesh")
            session.add(sample_cargo)
            session.commit()
            print("Sample data added: Kamalesh")

@app.on_event("startup")
def on_startup():
    init_db()

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Cargo Management API"}

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