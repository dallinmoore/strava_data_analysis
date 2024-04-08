# Data Analytics Project: Strava Activity Analysis

This repository contains a Python script (`main.py`) for analyzing running activities retrieved from the Strava API and stored in CSV format. The script performs various data analytics tasks, including data retrieval, data preprocessing, normalization, scoring, and result aggregation.

## Script Overview

### `main.py`

This script is designed to analyze running activities retrieved from the Strava API or from an existing CSV file (`running-data.csv`). It performs the following tasks:

1. **Data Retrieval**: Retrieves running activities data from the Strava API using authentication tokens. The retrieved data is stored in a list of dictionaries.

2. **Data Preprocessing and Storage**: Processes the retrieved data, calculates additional metrics, and stores the processed data in CSV format (`running-data.csv`).

3. **Normalization**: Normalizes selected columns in the dataset using z-score normalization.

4. **Effort Scoring**: Calculates an effort score for each activity based on predefined constants and selected metrics.

5. **Top Activities Analysis**: Identifies top activities based on various criteria such as effort score, distance, average speed, elevation gain, and average heart rate.

6. **Result Aggregation**: Aggregates the top activities analysis results into a JSON format and saves them to a file (`results.json`).

## Note

- This script is intended for educational and demonstration purposes and can be further extended or customized based on specific requirements.
- Ensure compliance with the Strava API terms of use and data privacy regulations while using this script.


---

*Disclaimer: This project is not affiliated with or endorsed by Strava. Use at your own risk.*
