import json
import os
import requests
import base64
from bs4 import BeautifulSoup
import re

# List of job titles to search for
berufe = ['Softwareentwickler',
        'Anwendungsentwickler',
        'Webentwickler',
        'Developer'
        ]

# Where
where = 'Berlin'

def get_jwt():
    """fetch the jwt token object"""
    headers = {
        'User-Agent': 'Jobsuche/2.9.2 (de.arbeitsagentur.jobboerse; build:1077; iOS 15.1.0) Alamofire/5.4.4',
        'Host': 'rest.arbeitsagentur.de',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
    }

    data = {
      'client_id': 'c003a37f-024f-462a-b36d-b001be4cd24a',
      'client_secret': '32a39620-32b3-4307-9aa1-511e3d7f48a8',
      'grant_type': 'client_credentials'
    }

    response = requests.post('https://rest.arbeitsagentur.de/oauth/gettoken_cc', headers=headers, data=data, verify=True)

    return response.json()

def search(jwt, what, where, size):
    """search for jobs. params can be found here: https://jobsuche.api.bund.dev/"""

    params = (
        ('angebotsart', '1'),
        ('page', '1'),
        ('pav', 'true'),
        ('size', size),
        ('umkreis', '200'),
        ('zeitarbeit', 'false'),
        ('veroeffentlichtseite', '100'),
        ('was', what),
        ('wo', where),
    )

    headers = {
        'User-Agent': 'Jobsuche/2.9.2 (de.arbeitsagentur.jobboerse; build:1077; iOS 15.1.0) Alamofire/5.4.4',
        'Host': 'rest.arbeitsagentur.de',
        'OAuthAccessToken': jwt,
        'Connection': 'keep-alive',
    }

    response = requests.get('https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/app/jobs',
                            headers=headers, params=params, verify=True)
    return response.json()

def find_emails(url):
    """Find all email addresses on a webpage"""
    # Send a GET request to the URL
    response = requests.get(url)
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')
    # Regular expression to match email addresses
    email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    # Find all strings in the page that match the regular expression
    emails = set(re.findall(email_regex, soup.get_text()))
    return emails

def get_externe_urls(jobs):
    """Get all externeUrls from the jobs"""
    urls = []
    for job in jobs.get('stellenangebote', []):
        if 'externeUrl' in job:
            urls.append(job['externeUrl'])
    return urls

def dump_emails(jobs):
    """Find emails in job descriptions and append them to a text file."""
    externe_urls = get_externe_urls(jobs)
    
    # Open or create the file before iterating over URLs
    with open('emails.txt', 'a', encoding='utf-8') as f:
        for url in externe_urls:
            emails = find_emails(url)  
            print(f"Found {len(emails)} emails on {url}")
            for email in emails:
                print(email)
                # Append each found email to the file
                f.write(email + '\n')

def dump_offeror(jobs):
    """Dump employer details to a JSON file, adding only new refnr entries."""
    
    # Attempt to load existing data from the file
    offeror_data = {}
    filename = 'refnr_offeror.json'
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            offeror_data = json.load(f)

    # Process new jobs and add them if refnr is not already in the file
    for job in jobs.get('stellenangebote', []):
        refnr = job['refnr']
        if refnr not in offeror_data:
            offeror_data[refnr] = {
                'arbeitgeber': job['arbeitgeber'],
                'beruf': job['beruf'],
                'arbeitsort': job['arbeitsort']['ort']
            }

    # Save the updated data back to the file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(offeror_data, f, indent=4)

def distinct_emails():
    """Remove duplicate emails from the file"""
    with open('emails.txt', 'r', encoding='utf-8') as f:
        emails = set(f.readlines())
    with open('emails.txt', 'w', encoding='utf-8') as f:
        f.writelines(emails)

def search_for_berufe(jwt, where, size):
    """Search for a list of job titles"""
    result = {}
    for beruf in berufe:
        result[beruf] = search(jwt["access_token"], beruf, where, size)
        # Output jobs
        print('Received ' + str(len(result[beruf]['stellenangebote'])) + ' jobs.')
        dump_emails(result[beruf])
        dump_offeror(result[beruf])
    return result

if __name__ == "__main__":
    jwt = get_jwt()
    result = search_for_berufe(jwt, where, 200)
    distinct_emails()
