import pandas as pd
from sklearn.model_selection import train_test_split
import sqlalchemy
from sqlalchemy import create_engine

# Shard configuration
SHARDS = {
    'shard_1': 'sqlite:///shard1.db',
    'shard_2': 'sqlite:///shard2.db',
    'shard_3': 'sqlite:///shard3.db'
}


def load_data(file_path):
    """
    Load data from a CSV file.
    """
    try:
        data = pd.read_csv(file_path)
        print("Data loaded successfully.")
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def clean_data(data):
    """
    Clean the dataset by handling missing values and duplicates.
    """
    # Drop duplicates
    data = data.drop_duplicates()

    # Fill missing values with mean for numerical columns
    for column in data.select_dtypes(include=['float64', 'int64']).columns:
        data[column].fillna(data[column].mean(), inplace=True)

    # Fill missing values with mode for categorical columns
    for column in data.select_dtypes(include=['object']).columns:
        data[column].fillna(data[column].mode()[0], inplace=True)

    print("Data cleaned successfully.")
    return data


def feature_engineering(data):
    """
    Perform feature engineering to create new features.
    """
    # Example: Create a feature for player efficiency
    if 'goals' in data.columns and 'minutes_played' in data.columns:
        data['efficiency'] = data['goals'] / data['minutes_played']
        data['efficiency'].fillna(0, inplace=True)

    print("Feature engineering completed.")
    return data


def split_data(data, target_column):
    """
    Split the data into training, validation, and test sets.
    """
    X = data.drop(columns=[target_column])
    y = data[target_column]

    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

    print("Data split into training, validation, and test sets.")
    return X_train, X_val, X_test, y_train, y_val, y_test


def get_shard(user_id):
    """
    Determine the shard based on the user ID.
    """
    shard_keys = list(SHARDS.keys())
    return SHARDS[shard_keys[user_id % len(shard_keys)]]


def save_to_shard(data, user_id):
    """
    Save data to the appropriate shard based on the user ID.
    """
    shard_url = get_shard(user_id)
    engine = create_engine(shard_url)

    with engine.connect() as connection:
        data.to_sql('processed_data', con=connection, if_exists='append', index=False)

    print(f"Data saved to shard: {shard_url}")


if __name__ == "__main__":
    # Example usage
    file_path = "data/player_performance.csv"  # Update with your file path
    target_column = "performance_metric"  # Update with your target column

    data = load_data(file_path)
    if data is not None:
        data = clean_data(data)
        data = feature_engineering(data)
        X_train, X_val, X_test, y_train, y_val, y_test = split_data(data, target_column)

        # Example: Save training data to shards based on user ID
        user_id = 123  # Replace with actual user ID logic
        save_to_shard(X_train, user_id)

        print("Processed data saved to shards.")