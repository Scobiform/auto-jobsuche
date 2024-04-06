import requests
import base64

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

def search(jwt, what, where):
    """search for jobs. params can be found here: https://jobsuche.api.bund.dev/"""

    params = (
        ('angebotsart', '1'),
        ('page', '1'),
        ('pav', 'true'),
        ('size', '100'),
        ('umkreis', '200'),
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

def get_job(jwt, refnr):
    """fetch job details"""
    
    headers = {
        'User-Agent': 'Jobsuche/2.9.2 (de.arbeitsagentur.jobboerse; build:1077; iOS 15.1.0) Alamofire/5.4.4',
        'Host': 'rest.arbeitsagentur.de',
        'OAuthAccessToken': jwt,
        'Connection': 'keep-alive',
    }

    response = requests.get(f'https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/app/jobs/{refnr}',
                            headers=headers, verify=True)
    return response.json()

def output_jobs(jobs):
    """print job details"""
    for job in jobs['stellenangebote']:
        print(job)

if __name__ == "__main__":
    jwt = get_jwt()
    result = search(jwt["access_token"], "", "berlin")
    # Dump jobs to dump.json
    with open('dump.json', 'w', encoding='utf-8') as f:
        f.write(str(result))
    # Output jobs
    output_jobs(result)
    print('Received ' + str(len(result['stellenangebote'])) + ' jobs.')