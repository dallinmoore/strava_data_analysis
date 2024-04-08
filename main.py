import requests
import json
import datetime
import pandas as pd
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

path = ""

# dictionary with the pertinent strings to access the api
payload = {
    'client_id': '116787',
    'client_secret': '',
    'refresh_token': '',
    'grant_type': 'refresh_token',
    'f': 'json'
}

# returns a list of dictionaries with all of the data received from the api
def update_data(payload=payload,end_page=1,start_page=1):
    data_list = []
    auth_url = "https://www.strava.com/oauth/token"
    activites_url = "https://www.strava.com/api/v3/athlete/activities"
    try:
        # the tokens expire so a new access_token must be generated
        print("Requesting access token...")
        res = requests.post(auth_url, data=payload, verify=False)
        access_token = res.json()['access_token']
        
        # using the access token, access 200 of my activities 
        header = {'Authorization': 'Bearer ' + access_token}
        print("Accessing Strava API...")
        for x in range(start_page,end_page+1):
            param = {'per_page': 200, 'page': x}
            dataset = requests.get(activites_url, headers=header, params=param).json()
            
            data_list += dataset

        return data_list
    except:
        raise Exception("Error accessing Strava API.")

# store the data in csv format, from a list of dictionaries containing all of the activities
def data_csv(json_data):
    print("Saving data to CSV...")
    data = []
    for x in json_data:
        if x["type"] == "Run":
            # Calculate idle_time as the difference between elapsed_time and moving_time
            idle_time = x["elapsed_time"] - x["moving_time"]
            
            # Ensure idle_time is non-negative; otherwise, set it to 0
            idle_time = max(idle_time, 0)
            
            start_datetime = datetime.datetime.strptime(x["start_date_local"], '%Y-%m-%dT%H:%M:%SZ')
            
            data.append([x["name"],
                        start_datetime.date(),  # Extract date from start_date
                        start_datetime.time(),  # Extract time from start_date
                        round(x["distance"] / 1609.344, 2),
                        float(idle_time),  # Convert idle_time to float
                        x["total_elevation_gain"],
                        round(x["average_speed"] * 2.23694, 2),
                        round(x["max_speed"] * 2.23694, 2),
                        x["average_heartrate"],
                        x["max_heartrate"]])
    
    df = pd.DataFrame(data, columns=['name', 'start_date', 'start_time', 'distance_miles', 'idle_time_seconds', 'elevation_gain', 'avg_speed_mph', 'max_speed_mph', 'avg_hr', 'max_hr']) 
    df.to_csv(path + "running-data.csv")
    return df

# takes in a df and a list of the columns that need to be normalized
# the metrics are assumed to be roughly normalized in order to use z-score normalization
def normalize(df_in, columns):
    print("Normalizing data...")
    # Check if all specified columns are present in the input DataFrame
    missing_columns = [col for col in columns if col not in df_in.columns]
    if missing_columns:
        raise ValueError(f"Columns {missing_columns} not found in the input DataFrame.")
    
    df_out = pd.DataFrame()
    
    for column in columns:
        # Calculate mean and standard deviation for the current column
        column_mean = df_in[column].mean()
        column_std = df_in[column].std()

        # Normalize the column and add to the output DataFrame
        df_out[column + '_zscore'] = (df_in[column] - column_mean) / column_std
    
    return df_out

# takes in a row and the appropriate constant values to weigh each column
# Composite score has the format: Effort Score=(a×Distance)+(b×Average Speed)+(cxMax Speed)+(d×Elevation)
def effort_score(df, constants):
    print("Calculating effort score...")
    # Ensure that the DataFrame has at least one column
    if len(df.columns) == 0:
        raise ValueError("DataFrame must have at least one column.")
    # Check if the number of columns matches the number of constants
    if len(df.columns) != len(constants):
        raise ValueError("Number of columns in the DataFrame does not match the number of constants.")
    
    # Calculate Effort Score for each row
    df_out = pd.DataFrame()
    df_out['Effort Score'] = round(sum(const * df[col] for col, const in zip(df.columns, constants)),3)
    return df_out

# return a json format dictionary with top activities based on one column
def top_activities(df, column, n=5, top=True):
    print(f"Finding top {column} activities...")
    # Check if the specified column exists in the DataFrame
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in the DataFrame.")

    # Get the top/bottom n rows based on the specified column
    if top:
        selected_rows = df.nlargest(n, column)
    else:
        selected_rows = df.nsmallest(n, column)

    # Convert 'start_date' column to datetime format
    selected_rows['start_date'] = pd.to_datetime(selected_rows['start_date'])

    # Initialize the summary dictionary
    summary = [{"Summary": {}}]

    # Calculate max value for each of the numeric columns
    for col in df.columns:
        if col != 'start_date' and pd.api.types.is_numeric_dtype(df[col]):
            max_value = df[col].max()
            summary[0]["Summary"][f"Max {col}"] = max_value

    # Convert the 'start_date' column to date only
    selected_rows['start_date'] = selected_rows['start_date'].dt.date

    # Calculate the average time between activities
    time_diff = selected_rows['start_date'].diff().mean()
    average_time_between = str(time_diff)

    summary[0]["Summary"]["Average time between"] = average_time_between

    # Convert the selected rows to a list of dictionaries
    result_list = summary + selected_rows.to_dict(orient='records')

    return result_list

# store results in a results.json 
def save_results(results):
    print("Saving to results.json...")
    with open(path+"results.json", "w") as results_file:
        # Convert Timestamp objects to strings before serializing to JSON
        results_json = json.dumps(results, default=str, indent=4)
        results_file.write(results_json)

def main():
    print("The Strava API can be accessed or existing data can be used from running-data.csv file.")
    if input("Update data?(y/n) ").lower().strip() == "y":
        df = data_csv(update_data())
    else:
        df = pd.read_csv(path+"running-data.csv",index_col=0)
    
    # can be changed to adjust what metrics are used and what the weights should be
    columns_used = ['distance_miles','elevation_gain','avg_speed_mph','max_speed_mph','avg_hr','max_hr','idle_time_seconds']
    constants_list = [.25,.15,.25,.05,.25,.1,-.05]
    
    df_normal = normalize(df,columns_used)
    df['effort_score'] = effort_score(df_normal, constants_list)
    
    json_out = {}
    json_out['Hardest Effort'] = top_activities(df,'effort_score')
    json_out['Longest Runs'] = top_activities(df,'distance_miles')
    json_out['Fastest Runs'] = top_activities(df,'avg_speed_mph')
    json_out['Most Elevation'] = top_activities(df,'elevation_gain')
    json_out['Highest Heartrate'] = top_activities(df,'avg_hr')
    
    save_results(json_out)
    print("Program complete.")


if __name__ == '__main__':
    main()
