# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 15:36:13 2024

@author: Pascaliensis with ChatGPT 3.4 and ChatGPT 4o

Version 0.10
"""


# This python script crawl a initial set of URLs written in a text file
# Every time the script is run, a csv file is produced with 3 columns :
#    - A column of the citing URL
#    - A column of the keywords found in the citing URL,
#    - A column of the cited URL
# Everytime the citing URL are checked to keep only the URL that are : blog and about TTRPG




import glob
import re
import pandas as pd
import csv
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import os.path
import time




def update_exclusion_list(exclusion_list_urls, url):
    # add this URL to exclusion list
    exclusion_list_urls.append(url)
    exclusion_list_urls = [url.strip() for url in exclusion_list_urls]
    exclusion_list_urls = list(set(exclusion_list_urls))
    # Open the file in write mode
    with open(exclusion_list_file, 'w', encoding='utf-8') as file:
        # Write each string in the list to the file
        for item in exclusion_list_urls:
            file.write(item + '\n')  # Add a newline character after each string


# this function strip a url to find its blog root web site
def rootify(url):
    parsed_url = urlparse(url)
    if    parsed_url.path.startswith("/blog/"):
          root_url = f"{parsed_url.scheme}://{parsed_url.netloc}/blog/"
    elif  parsed_url.path.startswith("/fr/blog/"):
          root_url = f"{parsed_url.scheme}://{parsed_url.netloc}/fr/blog/"
    elif  parsed_url.path.startswith("/en/blog/"):
          root_url = f"{parsed_url.scheme}://{parsed_url.netloc}/en/blog/"    
    elif  parsed_url.path.startswith("/article/"):
          root_url = f"{parsed_url.scheme}://{parsed_url.netloc}/article/" 
    elif  parsed_url.path.startswith("/articles/"):
          root_url = f"{parsed_url.scheme}://{parsed_url.netloc}/articles/" 
    else:
          root_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return root_url






# This function identifies if an URL is a blog and if it is about TTRPG 

def find_out(url, exclusion_list_urls, timeout=10, max_retries=3):
    
    # return the root of the website, 
    # except if the URL contains /blog/ after the root, in this case it return root/blog/
    root_url = rootify(url)
    
    # initialize the values that will be return with this function
    is_blog = False
    is_ttrpg_blog = False
    found_keywords = ''
    
    if root_url in exclusion_list_urls :
        
        print("")
        #result = [is_blog, is_ttrpg_blog, found_keywords]
        
    else : # if if root_url is NOT in exclusion_list
    
        for _ in range(max_retries):
            
            try:
                response = requests.get(root_url,timeout=timeout)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
            
                # 1. Try to identify if the website is a blog 
                blog_keywords = ['wordpress', 'blogger', 'tumblr', 'blogspot', 'medium', 'itch'
                                 'wix', 'squarespace', 'weebly', 'ghost', 'joomla', 'drupal', 'typepad',
                                 'substack', 'hubPages', 'github', 'gitlab', 'framagit', 'livejournal',
                                 'jekyll', 'hashnode', 'overblog', 'blog', 'canalblog', 'skyrock', 'svbtle']
                
                # 1.1 Check the <meta> tag with name="generator"
                meta_tag = soup.find('meta', {'name': 'generator'})
                # Check if the meta tag is present and contains any of the specified keywords (case-insensitive)
                if meta_tag:
                    content = meta_tag.get('content', '').lower()  # Convert content to lowercase
                    if any(keyword in content for keyword in blog_keywords):
                        is_blog = True
                
                # 1.2 Check the <link> tag for Atom or RSS feed indicator 
                atom_link = soup.find('link', {'rel': 'alternate', 'type': 'application/atom+xml'})
                rss_link = soup.find('link', {'rel': 'alternate', 'type': 'application/rss+xml'})
                if atom_link or rss_link:
                    is_blog = True
                
                # 1.3 Check with URL
                # Adding more keywords but just for the url 
                url_blog_keywords = ["article", 
                                     "articles",
                                     "post",
                                     "posts",]
                blog_keywords = blog_keywords + url_blog_keywords
                patterns = [re.compile(r'.*' + keyword + r'.*', re.IGNORECASE) for keyword in blog_keywords]
                # Check if any pattern matches the content in the URL
                if any(pattern.match(url) for pattern in patterns):
                    is_blog = True
                
                # 2. Try to identify if the content talk about TTRPG 
                if is_blog :
                    
                    # Remove all <a> tags and their content (to search within the text and not the <a>) 
                    for a_tag in soup.find_all('a'):
                        a_tag.decompose()
            
                    text = soup.get_text().lower()
                    
                    rpg_keywords = ['ttrpg', 'trpg', 'rpg', 'role-playing', 'roleplaying', 'role playing', 
                                    'jeu de rôle', 'jeux de rôle', 'rôliste', 
                                    'rolista', 'RPGista', 'juego de rol', 'juegos de rol', 'joc de rol',
                                    'rollenspiel', 'roolipeli', 'gioco di ruolo', 'ludus personarum',
                                    'gra fabularna', 'rollspel', 'рольова гра', 'permainan berperanan',
                                    'permainan bermain peran', 
                                    'gamemaster', 'game master', 'dungeon master', 
                                    'osr', 'd&d', 'the forge']
                    found_keywords = [keyword for keyword in rpg_keywords if keyword in text]
                    
                    if found_keywords:
                        is_ttrpg_blog = True    
                        
                    else : 
                        
                        # add this URL to exclusion list
                        exclusion_list_urls.append(root_url)
                        exclusion_list_urls = [root_url.strip() for root_url in exclusion_list_urls]
                        exclusion_list_urls = list(set(exclusion_list_urls))
                        
                
                else : 
                        # add this URL to exclusion list
                        exclusion_list_urls.append(root_url)
                        exclusion_list_urls = [root_url.strip() for root_url in exclusion_list_urls]
                        exclusion_list_urls = list(set(exclusion_list_urls))
                
                #result = [is_blog, is_ttrpg_blog, found_keywords]
                    
            except requests.RequestException as e:
                 print(f"Error fetching {root_url}: {e}")  
                 time.sleep(2)  # Delay before retrying
                 continue
                
                 #result = [is_blog, is_ttrpg_blog, str(e)] 
                 found_keywords = str(e)
                 
                 # add this URL to exclusion list
                 exclusion_list_urls.append(root_url)
                 exclusion_list_urls = [root_url.strip() for root_url in exclusion_list_urls]
                 exclusion_list_urls = list(set(exclusion_list_urls))
                    
    return is_blog, is_ttrpg_blog, found_keywords 















# MAIN PROGRAM



### Injecting URLs in the flow
# It supposed to be processed immediately at the beginning of the program
# After, it can be removed or left here (it is automatically ignored after beceuse it was processed)

urls_2_inject = [
    "https://www.prismaticwasteland.com",
    ]







### import data from the manual_URL

manual_url_list = 'manual_urls.txt'  # a text file with one URL per line
if os.path.exists(manual_url_list) :
    
    initial_citing_urls = []
    with open(manual_url_list, 'r', encoding='utf-8') as file:
        initial_citing_urls = file.readlines()
        
        # Remove '%0a' from the end of each URL
        for i in range(len(initial_citing_urls)):
            initial_citing_urls[i] = initial_citing_urls[i].rstrip('\n')
else: 
    initial_citing_urls = []





### import exclusion list (build up along the way by crawling)
# while doing it, remove the possible duplicates 

exclusion_list_file = 'exclusion_list.txt'  # a text file with one URL per line
exclusion_list_urls = []
if os.path.exists(exclusion_list_file) :
    with open(exclusion_list_file, 'r', encoding='utf-8') as file:
        exclusion_list_urls = file.readlines()
    # Strip newline characters and remove duplicates
    exclusion_list_urls = [url.strip() for url in exclusion_list_urls]
    exclusion_list_urls = list(set(exclusion_list_urls))

    # Write the unique URLs back to the file
    with open(exclusion_list_file, 'w', encoding='utf-8') as file:
        for url in exclusion_list_urls:
            file.write(url + '\n')







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



### import the data from the CSV

initial_csv_values = []

if highest_csv_file : 

    # Read the last csv iteration 
    df = pd.read_csv(highest_csv_file)
    # Optionally, convert the DataFrame to a dictionary, list, or other structure if needed
    initial_csv_values = df.to_dict(orient='records')  # Or use .to_list() for a list of rows, etc.
    # the result will be injected at the begining of the next iteration
    
    # Step 1: 
    # Filter non-empty 'CitedBlogURL' values
    # Integrating the previous initial URLs if existing
    
    initial_citing_urls = initial_citing_urls + df['CitedBlogURL'][df['CitedBlogURL'] != ''].tolist()
    
    # here are injected the URLs we want to add between two iterations
    initial_citing_urls = urls_2_inject + initial_citing_urls 
    
    # Step 2: Remove duplicates from initial_citing_urls
    # Remove the trailing "/" from each string in the list
    initial_citing_urls = [str(url).rstrip('/') for url in initial_citing_urls]
    initial_citing_urls = list(set(initial_citing_urls))  # Convert to set and back to list to remove duplicates
    # Step 3: Remove URLs found in df['CitingBlogURL']
    citing_urls_set = set(df['CitingBlogURL'].tolist())
    initial_citing_urls = [url for url in initial_citing_urls if url not in citing_urls_set]
    
    # Remove "nan" values from the list
    initial_citing_urls = [url for url in initial_citing_urls if not isinstance(url, float) and url != "nan"]


  




    
   
    
# Cleaning the initial_citing_urls :
#  -  from "bad" website (webscrapper traps that stuck you forever) 
#  -  or from bugs when the URL was retrieved 
# In case the process is stuck : 
#  1.  Add the problematic url from the console in the list under. 
#  2.  Restart the kernel of Python. 
#  3.  Restart the script.

# Set of URLs to remove
url_traps = {
    "No cited URL",
    "nan",
    "https://www.barnesandnoble.com",
    "http://www.barnesandnoble.com",
    "http://Agreenmanreview..come",
    "http://www.thinkgeek.com",
    "https://www.tripadvisor.com",
    "http://www.homedepot.com",
    "https://lurchundlama.de",
    "http://brandonsanderson.com",
    "https://docschottslab.wordpress.com",
    "hamsterhoard.blogspot.com",
    "http://www.canonfire.com",
} 
 
# Using list comprehension to create a new list without the URLs to remove
initial_citing_urls = [url for url in initial_citing_urls if url not in url_traps]    








# deprecated code : a list of URLs directly in the Python code  
#  
#initial_citing_urls = [
#    'https://jrients.blogspot.com',
#    'https://grognardia.blogspot.com',
#    'https://goblinpunch.blogspot.com',
#]








### Writing the next iteration while processing the URLs 

nb_URLs = len(initial_citing_urls)

print(f"This iteration starts with {nb_URLs} URLs to process.\n\n")


# Calculate the next integer
next_number = highest_number + 1

# Define the next csv file name
next_csv_file = f'blog_urls_iteration_{next_number}.csv'





# Write the header row once at the start if the file is empty
with open(next_csv_file, mode='a', encoding="utf-8", newline='') as file:
    writer = csv.DictWriter(file, fieldnames=['CitingBlogURL', 'CitingBlogKeywords', 'CitedBlogURL'])
    if file.tell() == 0:
        writer.writeheader()

if initial_csv_values:  # Write the rows from the previous iteration CSV
    for row in initial_csv_values:
        with open(next_csv_file, mode='a', encoding="utf-8", newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['CitingBlogURL', 'CitingBlogKeywords', 'CitedBlogURL'])
            writer.writerow(row)

cited_blog_urls = []

# Add new rows based on the initial_citing_urls
for citing_url in initial_citing_urls:

    root_citing_url = rootify(citing_url)
    print(f"\n\nExploring {citing_url} : ")

    citing_is_blog, citing_is_ttrpg_blog, citing_found_keywords = find_out(root_citing_url, exclusion_list_urls)
    
    if citing_is_ttrpg_blog: 

        # Retrieves the cited URL (pointing to other website than the citing URL)         
        try:
            response = requests.get(root_citing_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            cited_blog_urls = set()
            
            # retrieve a list of external URL that are blogs and that are about TTRPG 
            for a_tag in soup.find_all('a', href=True):
                cit_url = urljoin(root_citing_url, a_tag['href'])            
                root_cited_url = rootify(cit_url)
                
                if root_cited_url != root_citing_url :
                    
                        if root_cited_url not in exclusion_list_urls : 
                            # verify if the cited URL is a TTRPG blog
                            # if yes, integrates it in the list
                            try: 
                                cited_is_blog, cited_is_ttrpg_blog, cited_found_keywords = find_out(root_cited_url, exclusion_list_urls)
                            except:
                                cited_is_ttrpg_blog = False
                                
                                # updatye exclusion list
                                exclusion_list_urls.append(root_cited_url)
                                exclusion_list_urls = [root_cited_url.strip() for root_cited_url in exclusion_list_urls]
                                exclusion_list_urls = list(set(exclusion_list_urls))
                                
                            if cited_is_ttrpg_blog : 
                                cited_blog_urls.add(root_cited_url)
                                print(".", end="")
                        
                else: 
                        print("/", end="")
                        # updatye exclusion list
                        exclusion_list_urls.append(root_cited_url)
                        exclusion_list_urls = [root_cited_url.strip() for root_cited_url in exclusion_list_urls]
                        exclusion_list_urls = list(set(exclusion_list_urls))
        
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")

        
        if cited_blog_urls : 
            
            for cited_url in cited_blog_urls:
                with open(next_csv_file, mode='a', encoding="utf-8", newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=['CitingBlogURL', 'CitingBlogKeywords', 'CitedBlogURL'])
                    writer.writerow({
                                        'CitingBlogURL': root_citing_url,
                                        'CitingBlogKeywords': citing_found_keywords,
                                        'CitedBlogURL': cited_url
                                    })

        else : 
            with open(next_csv_file, mode='a', encoding="utf-8", newline='') as file:
                writer = csv.DictWriter(file, fieldnames=['CitingBlogURL', 'CitingBlogKeywords', 'CitedBlogURL'])
                writer.writerow({
                                    'CitingBlogURL': root_citing_url,
                                    'CitingBlogKeywords': citing_found_keywords,
                                    'CitedBlogURL': "no TTRPG blog cited"
                                })

    else: 
        if citing_found_keywords : 
            # in fact, its asking "do there is a error message in citing_found_keywords?"
            data = {
                'CitingBlogURL': root_citing_url,
                'CitingBlogKeywords': f"not TTRPG blog or {citing_found_keywords}",
                'CitedBlogURL': ""
            }

        else : 
            data = {
                'CitingBlogURL': root_citing_url,
                'CitingBlogKeywords': "not TTRPG blog",
                'CitedBlogURL': ""
            }
        with open(next_csv_file, mode='a', encoding="utf-8", newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['CitingBlogURL', 'CitingBlogKeywords', 'CitedBlogURL'])
            writer.writerow(data)

    # write the updated exclusion list
    with open(exclusion_list_file, 'w', encoding='utf-8') as file:
        # Write each string in the list to the file
        for item in exclusion_list_urls:
            file.write(item + '\n')  # Add a newline character after each string
