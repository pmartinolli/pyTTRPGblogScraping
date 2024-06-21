# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 21:32:56 2024

@author: pascaliensis, with chatGPT 3.5 et 4o
"""

import pandas as pd
import glob
import re


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











# Replace 'highest_csv_file' with your csv file path
df = pd.read_csv(highest_csv_file)
# Now 'df' is a DataFrame with the first row of 'file.csv' as column names





# Strip "http://" and "https://" and "www."
df['CitingBlogURL'] = df['CitingBlogURL'].str.replace('http://', '').str.replace('https://', '').str.replace('www.', '')
df['CitedBlogURL'] = df['CitedBlogURL'].str.replace('http://', '').str.replace('https://', '').str.replace('www.', '')

# Remove everything after the last dot 
df['CitingBlogURL'] = df['CitingBlogURL'].apply(lambda x: x.rsplit('.', 1)[0] if isinstance(x, str) and '.' in x else x)
df['CitedBlogURL'] = df['CitedBlogURL'].apply(lambda x: x.rsplit('.', 1)[0] if isinstance(x, str) and '.' in x else x)

# Split on "blogspot" and keep only the part before it
df['CitingBlogURL'] = df['CitingBlogURL'].apply(lambda x: x.split('blogspot')[0] + 'blogspot' if isinstance(x, str) and 'blogspot' in x else x)
df['CitedBlogURL'] = df['CitedBlogURL'].apply(lambda x: x.split('blogspot')[0] + 'blogspot' if isinstance(x, str) and 'blogspot' in x else x)



# Remove the rows where "Not TTRPG blog..." 
df = df[~df['CitingBlogKeywords'].str.startswith('not TTRPG blog')]
df = df[~df['CitingBlogKeywords'].str.startswith('no TTRPG blog cited')]

# Remove the rows where Citing = Cited
df = df[df['CitingBlogURL'] != df['CitedBlogURL']]

# Remove duplicates rows based on Citing / Cited pairs
df = df.drop_duplicates(subset=['CitingBlogURL', 'CitedBlogURL'])

# Rename columns
df = df.rename(columns={'CitingBlogURL': 'Source', 'CitedBlogURL': 'Target'})


df.to_csv('clean_citing_cited_TTRPG_blog_list.csv', index=False)

print("\nCSV cleaned and exported")
