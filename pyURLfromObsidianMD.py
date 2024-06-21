# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 22:30:55 2024

@author: pascaliensis, with chatGPT 3.5 et 4o
"""

# prompt : i want you to crawl a folder and all its subfolders and for each .md file found inside, extract and collect all URL into a text file (one by line)


import os
import re
from urllib.parse import urlparse



# Function to extract URLs from a Markdown file
def extract_urls_from_md(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
        return urls

# Function to crawl through a directory and collect URLs from .md files
def crawl_and_collect_urls(root_folder, output_file):
    with open(output_file, 'w', encoding='utf-8') as output:
        for root, dirs, files in os.walk(root_folder):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    urls = extract_urls_from_md(file_path)
                    for url in urls:
                        output.write(url + '\n')
                        print(".", end="")

# Example usage
root_folder = r'C:\Users\pascaliensis\ObsidianV\TTRPGconseils'  # Replace with your actual root folder path
output_file = 'extracted_urls.txt'
processed_file = 'processed_urls.txt' 
final_file = 'manual_urls.txt'

crawl_and_collect_urls(root_folder, output_file)


def remove_after_brackets(input_string):
    # Define characters to look for
    chars_to_look_for = ['[', ']', '(', ')']

    # Iterate through each character and find its index
    for char in chars_to_look_for:
        if char in input_string:
            index = input_string.index(char)
            input_string = input_string[:index]

    return input_string.strip()  # Remove leading/trailing whitespace if necessary

# Function to process each URL read from the file
def process_url_line(line):
    line = remove_after_brackets(line) 
    
    # Regular expression pattern to match blogspot.XXX and replace by blogspot.com
    pattern = r'blogspot\.[a-zA-Z0-9.-]+'
    # Replace occurrences using re.sub()
    line = re.sub(pattern, 'blogspot.com', line)
    
    # Example treatment: Append 'processed_' to the beginning of each URL
    parsed_url = urlparse(line)
    if parsed_url.path.startswith("/blog/"):
        root_citing_url = f"{parsed_url.scheme}://{parsed_url.netloc}/blog/"
    else:
        root_citing_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return root_citing_url


# Function to read the file, apply process_url_line for each line, and write to a new file
def process_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as input_f, open(output_file, 'w', encoding='utf-8') as output_f:
        for line in input_f:
            processed_line = process_url_line(line)
            output_f.write(processed_line + '\n')


process_file(output_file, processed_file)



# remove duplicates lines

def deduplicate(input_file, output_file):
    # Read lines from input file
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Sort lines alphabetically
    sorted_lines = sorted(set(lines))  # Using set to remove duplicates and then sorting
    
    # Write sorted and deduplicated lines to output file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines(sorted_lines)
        
        
        
        
deduplicate(processed_file, final_file)        

