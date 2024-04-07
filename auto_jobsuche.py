import json
import requests
import base64
from bs4 import BeautifulSoup
import re

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

def output_jobs(jobs):
    """print job details"""
    for job in jobs['stellenangebote']:
        print(job)

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
    """Find emails in job descriptions and save them to a JSON file."""
    externe_urls = get_externe_urls(jobs)
    email_data = {}

    # Iterate over all external URLs and find emails on each page
    for url in externe_urls:
        emails = find_emails(url)  
        print(f"Found {len(emails)} emails on {url}")
        for email in emails:
            print(email)
        email_data[url] = list(emails)

    # Save all emails and their corresponding URLs to a JSON file
    with open('emails.json', 'w') as f:
        json.dump(email_data, f, indent=4)

def dump_offeror(jobs):
    """Dump employer details to a JSON file"""
    offeror_data = {}
    for job in jobs.get('stellenangebote', []):
        offeror_data[job['refnr']] = job['arbeitgeber']
    with open('refnr_offeror.json', 'w') as f:
        json.dump(offeror_data, f, indent=4 )

if __name__ == "__main__":
    jwt = get_jwt()
    result = search(jwt["access_token"], "Softwareentwickler", "berlin", "200")
    # Output jobs
    output_jobs(result)
    print('Received ' + str(len(result['stellenangebote'])) + ' jobs.')
    # Dump emails
    dump_emails(result)
    # Dump offeror details
    dump_offeror(result)
