import pandas as pd

# list of data files.
detection_files = [
    "data/2018/Master_Manual_9M_2h_2018.xlsx",
    "data/2018/Master_Manual_14M_2h_2018.xlsx",
    "data/2018/Master_Manual_37M_2h_2018.xlsx",
    "data/2021/Master_Manual_9M_2h_2021.xlsx",
    "data/2021/Master_Manual_14M_2h_2021.xlsx",
    "data/2021/Master_Manual_37M_2h_2021.xlsx",
]

columns_file = "data/det_column_names.csv"

# Load the CSV file and convert the specified columns into a dictionary
def load_and_convert_to_dict(file_path):
    df = pd.read_csv(file_path)
    return dict(zip(df["short_name"], df["long_name"]))

column_lookup = load_and_convert_to_dict(columns_file)
short_column_names = list(column_lookup.keys())
long_column_names = list(column_lookup.values())

# Load all detection files into a single dataframe
all_dfs = []
for file in detection_files:
    df_ = pd.read_excel(file, sheet_name=1)
    df_.columns = short_column_names
    # Extract year and station from filename
    parts = file.split('/')
    year = parts[1]
    station = parts[2].split('_')[2]
    df_['year'] = year
    df_['station'] = station
    all_dfs.append(df_)

combined_df = pd.concat(all_dfs, ignore_index=True)
combined_df['date'] = pd.to_datetime(combined_df['date'])

combined_df.to_csv('combined_df_export.csv', index=False)
