import pandas as pd #using this as it simplifies handling and processing tabular data
import random #using this in order to select a random entry in the csv file to start from
import os #using this in order to interact with the host

# Function to get 10 random consecutive data points from a csv file without headers
def get_random_10_consecutive_data_points(file_path):
    # Read the CSV file without headers
    df = pd.read_csv(file_path, header=None)
    
    # Manually assign column names
    df.columns = ['Stock-ID', 'Timestamp', 'stock_price']
    
    # Convert the Timestamp column to datetime
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%d-%m-%Y')
    
    # Sort by Timestamp
    df = df.sort_values(by='Timestamp')
    
    # Determine a random start index to select 10 consecutive data points
    max_start_index = len(df) - 10
    if max_start_index <= 0:
        return None  # Not enough data points
    
    start_index = random.randint(0, max_start_index)
    random_10_data_points = df.iloc[start_index:start_index + 10].reset_index(drop=True)
    
    return random_10_data_points

# Function to predict the next 3 values
def predict_next_3_values(data_points):
    stock_prices = data_points['stock_price'].values
    n_plus_1 = sorted(stock_prices)[-2]
    n_plus_2 = n_plus_1 + 0.5 * (n_plus_1 - stock_prices[-1])
    n_plus_3 = n_plus_2 + 0.25 * (n_plus_2 - n_plus_1)
    return [n_plus_1, n_plus_2, n_plus_3]

# Function to save predictions to CSV
def save_predictions_to_csv(stock_id, data_points, predictions, output_dir):
    # Convert the Timestamp column in data_points to the desired format
    data_points['Timestamp'] = data_points['Timestamp'].dt.strftime('%d-%m-%Y')

    # Generate new timestamps for the predictions, ensuring they are in the correct format
    last_date = pd.to_datetime(data_points['Timestamp'].iloc[-1], format='%d-%m-%Y')
    prediction_timestamps = pd.date_range(start=last_date, periods=4, freq='D')[1:]
    prediction_timestamps = prediction_timestamps.strftime('%d-%m-%Y')

    # Create a DataFrame for the predictions
    prediction_df = pd.DataFrame({
        'Stock-ID': [stock_id] * 3,
        'Timestamp': prediction_timestamps,
        'stock_price': predictions
    })
    
    # Combine the original data points and the predictions
    combined_df = pd.concat([data_points, prediction_df], ignore_index=True)

    # Save the combined data to a CSV file
    output_file = os.path.join(output_dir, f"{stock_id}_predictions.csv")
    combined_df.to_csv(output_file, index=False)
    print(f"Saved predictions to {output_file}")

# Function to list files excluding unwanted ones
def list_files(directory):
    return [f for f in os.listdir(directory) if not f.startswith('.')]

# Function to process stock exchanges
def process_stock_exchanges(stock_data_dir, num_files_to_sample=1, output_dir='./output'):
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Dynamically get the list of exchange directories (folders)
    exchanges = [d for d in os.listdir(stock_data_dir) if os.path.isdir(os.path.join(stock_data_dir, d))]
    
    for exchange in exchanges:
        exchange_dir = os.path.join(stock_data_dir, exchange)
        files = list_files(exchange_dir)
        
        if not files:
            print(f"The folder '{exchange}' is empty.")
            continue
        
        files = files[:num_files_to_sample]

        for file_name in files:
            file_path = os.path.join(exchange_dir, file_name)
            stock_id = file_name.split('.')[0]
            
            data_points = get_random_10_consecutive_data_points(file_path)
            if data_points is not None:
                predictions = predict_next_3_values(data_points)
                save_predictions_to_csv(stock_id, data_points, predictions, output_dir)

# Main entry point
if __name__ == '__main__':
    stock_data_dir = './stock_price_data_files'  # Path to the data folder holding the initial stock info
    output_dir = './output'  # Output directory for predictions
    process_stock_exchanges(stock_data_dir, num_files_to_sample=2, output_dir=output_dir)
