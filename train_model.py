import pandas as pd
import psycopg2
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import mlflow
import mlflow.sklearn

# 1. Connection configuration to Postgres
DB_PARAMS = {
    "host": "localhost",
    "database": "smart_efuse_data",
    "user": "admin",
    "password": "password123",
    "port": "5432"
}

def load_data_from_warehouse():
    """Connects to Postgres and reads telemetry into a Pandas DataFrame."""
    conn = psycopg2.connect(**DB_PARAMS)
    query = "SELECT current, voltage, speed, fault FROM fuse_telemetry;"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def train_and_track():
    # TELL LOCAL SCRIPT TO TALK TO DOCKER CONTAINER MLFLOW
    mlflow.set_tracking_uri("http://localhost:5000")
    
    # Set the name of our machine learning experiment
    mlflow.set_experiment("Smart_eFuse_Predictive_Maintenance")
    
    print("Fetching data from the warehouse...")
    # Set the name of our machine learning experiment in MLflow
    mlflow.set_experiment("Smart_eFuse_Predictive_Maintenance")

    print("Fetching data from the warehouse...")
    df = load_data_from_warehouse()
    
    if len(df) < 10:
        print(" Error: Not enough data in the database yet. Run ingest_data.py for a bit longer!")
        return

    # Split data into features (X) and target label (y)
    X = df[['current', 'voltage', 'speed']]
    y = df['fault']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Define hyperparameters for our model
    n_estimators = 50
    max_depth = 5

    # Start an MLflow tracking session
    with mlflow.start_run():
        print("Training model...")
        model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
        model.fit(X_train, y_train)

        # Make predictions and calculate metrics
        predictions = model.predict(X_test)
        acc = accuracy_score(y_test, predictions)
        f1 = f1_score(y_test, predictions, zero_division=0)
        precision = precision_score(y_test, predictions, zero_division=0)
        recall = recall_score(y_test, predictions, zero_division=0)

        print(f"Model Trained! Metrics -> Accuracy: {acc:.2f} | F1-Score: {f1:.2f}")

        # --- LOG TO MLFLOW ---
        # 1. Log hyperparameters
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)

        # 2. Log performance metrics
        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("f1_score", f1)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)

        # 3. Log the trained model artifact itself
        mlflow.sklearn.log_model(model, "predictive_maintenance_rf_model")
        
        print(" Successfully logged parameters, metrics, and model artifact to MLflow!")

if __name__ == "__main__":
    train_and_track()