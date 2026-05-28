from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow
import mlflow.pyfunc
import pandas as pd

app = FastAPI(title="Smart e-Fuse Predictive Maintenance API", version="1.0")

# Define the structure of incoming sensor data using Pydantic
class TelemetryInput(BaseModel):
    current: float
    voltage: float
    speed: float

# Global variable to hold our loaded model
model = None


@app.on_event("startup")
def load_latest_model():
    """Triggered when FastAPI starts up. Programmatically pulls the best model from MLflow."""
    global model
    model_uri = None  # Pre-define to prevent UnboundLocalError
    
    try:
        # Initialize MLflow tracking connection
        # Tell FastAPI to look for MLflow on the docker network service named 'mlflow_server'
        mlflow.set_tracking_uri("http://mlflow_server:5000")
        mlflow.set_experiment("Smart_eFuse_Predictive_Maintenance")
        
        # Search for the latest successful runs
        runs = mlflow.search_runs(experiment_names=["Smart_eFuse_Predictive_Maintenance"])
        
        if runs.empty:
            print(" Error: No logged MLflow runs found! Did you run train_model.py?")
            model = None
            return
        
        # Grab the run ID of the most recent training execution
        latest_run_id = runs.iloc[0]['run_id']
        
        # Correct MLflow URI format format is runs:/<run_id>/<artifact_path>
        model_uri = f"runs:/{latest_run_id}/predictive_maintenance_rf_model"
        
        print(f"📦 Attempting to load model from URI: {model_uri}")
        model = mlflow.pyfunc.load_model(model_uri)
        print(" Model successfully loaded into memory and ready for inference!")
        
    except Exception as e:
        print(f" Actual underlying error during startup: {str(e)}")
        if model_uri:
            print(f" Failed while attempting to access URI: {model_uri}")
        model = None

@app.get("/")
def health_check():
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/predict")
def predict_fault(data: TelemetryInput):
    """Exposes an endpoint to accept sensor data and return a prediction."""
    if model == None:
        raise HTTPException(status_code=503, detail="Model is not initialized or failed to load.")
    # Convert incoming JSON data into a DataFrame layout matching training format
    input_df = pd.DataFrame([{
        'current': data.current,
        'voltage': data.voltage,
        'speed': data.speed
    }])

    # Run inference
    prediction = model.predict(input_df)

    # Convert prediciton to standard Python integer

    fault_status = int(prediction[0])

    # Return structured JSON response back to client
    return {
        "prediction": fault_status,
        "status": "CRITICAL_FAULT_WARNING" if fault_status == 1 else "OPERATIONAL_NORMAL"
    }