"""Some doc string
"""


import json
import os
import requests as r
from requests.auth import HTTPBasicAuth
import time


PROJECT_ROOT_PATH = os.environ.get('PROJECT_ROOT_PATH')
SLEEP_TIME = 60

BASE_URL = 'https://photoai.lotlinx.com'

DEALER_ID = 1       # arbitrary
VEHICLE_ID = 7416   # arbitrary


def submit_requests(auth, images):
    _path = 'images/optimize'

    body = {
        'dealerId': DEALER_ID,
        'vehicles':[
            {
                'id': VEHICLE_ID,
                'images' : list()
            }
        ]
    }

    for image in images:
        body['vehicles'][0]['images'].append({
            'imageId': image['id'],
            'imageUrl': image['url']
        })

    return r.post('%s/%s' % (BASE_URL, _path), json=body, auth=auth)


def check_status(auth, token):
    _path = 'images/%s/status' % token

    return r.get('%s/%s' % (BASE_URL, _path), auth=auth)


def load_response(auth, token):
    _path = 'images/%s' % token

    return r.get('%s/%s' % (BASE_URL, _path), auth=auth)


if __name__ == '__main__':
    credentials = json.load(open('%s/inputs/credentials.json' % PROJECT_ROOT_PATH))
    auth = HTTPBasicAuth(credentials['username'], credentials['password'])

    images = json.load(open('%s/inputs/images.json' % PROJECT_ROOT_PATH))

    state = 'submit_requests'
    status_code = None
    request_status = None
    token = None
    optimized_images = None

    while True:
        print('state: %s' % state)

        if state == 'submit_requests':
            resp = submit_requests(auth, images)
            status_code = resp.status_code

            state = 'check_status'

        if state == 'check_status':
            if status_code != 200:
                raise Exception('%s - %s' % (status_code, resp.json()['meta']['errorMsg']))
            else:
                body = resp.json()['data'][0]
                request_status = body['status']
                token = body['token']

                print('request_status: %s' % request_status)
                print('token: %s' % token)

                if request_status == 'complete':
                    resp = load_response(auth, token)
                    optimized_images = resp.json()['data'][0]['vehicles'][0]['images']

                    break
                elif request_status == 'failed':
                    state = 'submit_requests'
                elif request_status == 'queued':
                    print('Queued. Sleeping for a minute.')
                    time.sleep(SLEEP_TIME)
                    resp = check_status(auth, token)

    if optimized_images:
        if not os.path.exists('%s/outputs' % PROJECT_ROOT_PATH):
            os.makedirs('%s/outputs' % PROJECT_ROOT_PATH)

        with open('%s/outputs/optimized_images.json' % PROJECT_ROOT_PATH, 'w') as file:
            json.dump(optimized_images, file, indent=4)

        for image in optimized_images:
            image_id = image['imageId']
            modified_url = image['modifiedUrl']

            resp = r.get(modified_url, allow_redirects=True)
            with open('%s/outputs/optimized_image_%d.png' % (PROJECT_ROOT_PATH, image_id), 'wb') as file:
                file.write(resp.content)
