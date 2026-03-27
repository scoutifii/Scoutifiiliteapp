import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib


def load_processed_data():
    """
    Load processed training, validation, and test datasets.
    """
    try:
        X_train = pd.read_csv("data/X_train.csv")
        X_val = pd.read_csv("data/X_val.csv")
        X_test = pd.read_csv("data/X_test.csv")
        y_train = pd.read_csv("data/y_train.csv").values.ravel()
        y_val = pd.read_csv("data/y_val.csv").values.ravel()
        y_test = pd.read_csv("data/y_test.csv").values.ravel()

        print("Processed data loaded successfully.")
        return X_train, X_val, X_test, y_train, y_val, y_test
    except Exception as e:
        print(f"Error loading processed data: {e}")
        return None, None, None, None, None, None


def train_model(X_train, y_train, X_val, y_val):
    """
    Train a Random Forest model and evaluate it on the validation set.
    """
    try:
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # Evaluate on validation set
        y_val_pred = model.predict(X_val)
        val_rmse = mean_squared_error(y_val, y_val_pred, squared=False)
        val_r2 = r2_score(y_val, y_val_pred)

        print(f"Validation RMSE: {val_rmse}")
        print(f"Validation R2 Score: {val_r2}")

        return model
    except Exception as e:
        print(f"Error training model: {e}")
        return None


def evaluate_model(model, X_test, y_test):
    """
    Evaluate the trained model on the test set.
    """
    try:
        y_test_pred = model.predict(X_test)
        test_rmse = mean_squared_error(y_test, y_test_pred, squared=False)
        test_r2 = r2_score(y_test, y_test_pred)

        print(f"Test RMSE: {test_rmse}")
        print(f"Test R2 Score: {test_r2}")
    except Exception as e:
        print(f"Error evaluating model: {e}")


def save_model(model, file_path):
    """
    Save the trained model to a file.
    """
    try:
        joblib.dump(model, file_path)
        print(f"Model saved to {file_path}")
    except Exception as e:
        print(f"Error saving model: {e}")


if __name__ == "__main__":
    # Load processed data
    X_train, X_val, X_test, y_train, y_val, y_test = load_processed_data()

    if X_train is not None:
        # Train the model
        model = train_model(X_train, y_train, X_val, y_val)

        if model is not None:
            # Evaluate the model
            evaluate_model(model, X_test, y_test)

            # Save the model
            save_model(model, "models/player_performance_model.pkl")