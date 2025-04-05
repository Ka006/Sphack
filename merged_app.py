from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, List, Any

app = FastAPI()

# ------------------- CHATGPT2.PY Functionality -------------------

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

@app.get("/expanded-items")
def get_expanded_items():
    """Retrieve the expanded items dictionary."""
    return expanded_items_dict

# ------------------- COPIOLT.PY Functionality -------------------

# In-memory storage for demonstration purposes
storage: Dict[str, Dict] = {}

class StorageItem(BaseModel):
    id: str
    name: str
    value: str

class UpdateStorageItem(BaseModel):
    name: Optional[str] = None
    value: Optional[str] = None

@app.post('/storage', response_model=Dict[str, str])
def create_storage(item: StorageItem):
    if item.id in storage:
        raise HTTPException(status_code=400, detail="Storage already exists")
    storage[item.id] = item.dict()
    return {"message": "Storage created successfully"}

@app.get('/storage/{storage_id}', response_model=Dict)
def retrieve_storage(storage_id: str):
    if storage_id not in storage:
        raise HTTPException(status_code=404, detail="Storage not found")
    return storage[storage_id]

@app.put('/storage/{storage_id}', response_model=Dict[str, str])
def update_storage(storage_id: str, item: UpdateStorageItem):
    if storage_id not in storage:
        raise HTTPException(status_code=404, detail="Storage not found")
    if item.name is not None:
        storage[storage_id]['name'] = item.name
    if item.value is not None:
        storage[storage_id]['value'] = item.value
    return {"message": "Storage updated successfully"}

@app.delete('/storage/{storage_id}', response_model=Dict[str, str])
def delete_storage(storage_id: str):
    if storage_id not in storage:
        raise HTTPException(status_code=404, detail="Storage not found")
    del storage[storage_id]
    return {"message": "Storage deleted successfully"}

@app.get('/storage', response_model=List[Dict])
def list_storage():
    return list(storage.values())

@app.get('/storage/search', response_model=List[Dict])
def search_storage(name: Optional[str] = None, value: Optional[str] = None):
    results = []
    for item in storage.values():
        if name and item['name'] == name:
            results.append(item)
        elif value and item['value'] == value:
            results.append(item)
    return results

# ------------------- Application Startup -------------------

@app.get("/")
def read_root():
    return {"message": "Welcome to the Merged FastAPI Application"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)