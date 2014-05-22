import os
import json
import requests
import multiprocessing

cwd = os.path.dirname(os.path.realpath(__file__))
num_requests = 3
key = ''
headers = {'Cache-Control' : 'no-cache'}
post_url = ''

def get_code(url):
    # Try loaing the site in 1 second
    try:
        requests.get(url, timeout=1, headers=headers, verify=False)
        return 1
    except: pass

    # Try loaing the site in 3 seconds
    try:
        requests.get(url, timeout=5, headers=headers, verify=False)
        return 3
    except: pass

    # Try loaing the site in 12 seconds
    try:
        requests.get(url, timeout=12, headers=headers, verify=False)
        return 10
    except: return 30

def check(site):
    code = 0
    for i in xrange(num_requests):
        code += get_code(site['url'])
    
    params = {'name': site['name'], 'key': key}

    if 3 <= code <= 5:
        print '%s|GREEN' % site['name']
        params['status'] = 'GREEN'
        requests.post(post_url, params=params)
    elif 6 <= code <= 30:
        print '%s|AMBER' % site['name']
        params['status'] = 'AMBER'
        requests.post(post_url, params=params)
    elif code > 30:
        print '%s|RED' % site['name']
        params['status'] = 'RED'
        requests.post(post_url, params=params)

if __name__ == '__main__':
    # Load up the JSON file
    file_path = os.path.join(cwd, 'banks.json')
    banks = json.loads(open(file_path).read())

    # Create a list of banks to check
    bank_list = []
    for bank, meta in banks.iteritems():
        bank_list.append({
            'name': bank,
            'url': meta['url']
        })

    # Process the files, determine canidates for clustering
    pool = multiprocessing.Pool(processes=2)
    pool.map(check, bank_list)