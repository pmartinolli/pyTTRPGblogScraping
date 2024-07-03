# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 09:47:48 2024

@author: martinop
"""




import glob
import re
import pandas as pd
 



# Try to find a previous CSV produced by the program. 
#    If previous iterations are found then select the highest iteration 
#    If not then load a text file named "final_urls.txt"

# Pattern of the csv files
pattern = 'blog_urls_iteration_*.csv'

# Get a list of all csv files
csv_files = glob.glob(pattern)

# Initialize a variable to store the highest number
highest_csv_file = ''
highest_number = 0

# Check if there are any csv files
if csv_files:   
    
    # Loop through all csv files
    for file in csv_files:
        # Extract the number from the file name using regex
        match = re.search(r'blog_urls_iteration_(\d+)\.csv', file)

        # Check if a match was found
        if match is not None:
            number = int(match.group(1))

            # Update the highest number and file name if necessary
            if number > highest_number:
                highest_number = number
                highest_csv_file = file

    print(f"The file with the highest number in its name is: {highest_csv_file}")
else:
    print("No CSV files found.")






# List of unwanted URLs to remove
unwanted_urls = {
    "mailto:",
    "mailto://ksbdabbadon@gmail.com",
    "no TTRPG blog cited",
    "tel:",
    "ttps://danhunsaker.awswan.com",
    "about:",
    "feed:",
    "http:",
}










### import the data from the CSV

initial_csv_values = []

# Check if the highest_csv_file variable is defined and not None

if highest_csv_file:
    # Read the last CSV iteration
    df = pd.read_csv(highest_csv_file)

    # Optionally, convert the DataFrame to a dictionary if needed
    initial_csv_values = df.to_dict(orient='records')

    # Extract 'CitedBlogURL' column and convert to a set to remove duplicates
    initial_urls_set = set(df['CitedBlogURL'].tolist())

    # Extract 'CitingBlogURL' column and convert to a set
    citing_urls_set = set(df['CitingBlogURL'].tolist())

    # Remove the trailing "/" from each string in the sets
    initial_urls_set = {str(url).rstrip('/') for url in initial_urls_set}
    citing_urls_set = {str(url).rstrip('/') for url in citing_urls_set}

    # Remove "nan" values from the sets
    initial_urls_set = {url for url in initial_urls_set if not isinstance(url, float) and url != "nan"}
    citing_urls_set = {url for url in citing_urls_set if not isinstance(url, float) and url != "nan"}

    # Remove values found in citing_urls_set from initial_urls_set
    initial_urls_set -= citing_urls_set
    
    # Remove unwanted URLs
    initial_urls_set -= unwanted_urls

    # Convert the set to a list and sort it
    initial_urls_list = sorted(initial_urls_set)

    # Write the URLs to a text file, each value on a new line
    with open('iterationX_urls.txt', 'w') as file:
        for url in initial_urls_list:
            file.write(url + '\n')

    print("iterationX_urls.txt created")
    
    
    