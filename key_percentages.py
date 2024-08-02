import pandas as pd

def calculate_new_projects(total_df, filtered_df):
    # Convert dates to datetime if not already
    total_df['date_of_build'] = pd.to_datetime(total_df['date_of_build'])
    filtered_df['date_of_build'] = pd.to_datetime(filtered_df['date_of_build'])
    
    # Get the date range of the filtered dataset
    start_date = filtered_df['date_of_build'].min()
    end_date = filtered_df['date_of_build'].max()
    
    # Determine new projects
    existing_projects_before_filter = total_df[total_df['date_of_build'] < start_date]['projname'].unique()
    new_projects = filtered_df[~filtered_df['projname'].isin(existing_projects_before_filter)]['projname'].nunique()
    
    return new_projects

def calculate_new_developers(total_df, filtered_df):
    # Convert dates to datetime if not already
    total_df['date_of_build'] = pd.to_datetime(total_df['date_of_build'])
    filtered_df['date_of_build'] = pd.to_datetime(filtered_df['date_of_build'])
    
    # Get the date range of the filtered dataset
    start_date = filtered_df['date_of_build'].min()
    end_date = filtered_df['date_of_build'].max()
    
    # Determine new developers
    developer_first_appearances = total_df.groupby('user_id')['date_of_build'].min()
    new_developers = developer_first_appearances[
        (developer_first_appearances >= start_date) & (developer_first_appearances <= end_date)
    ].count()
    
    return new_developers
