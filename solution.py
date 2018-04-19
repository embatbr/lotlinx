"""Some doc string
"""


import json
import logging
import os
import requests as r
from requests.auth import HTTPBasicAuth
import time


PROJECT_ROOT_PATH = os.environ.get('PROJECT_ROOT_PATH')
SLEEP_TIME = 60

BASE_URL = 'https://photoai.lotlinx.com'

DEALER_ID = 1       # arbitrary
VEHICLE_ID = 7416   # arbitrary


logger = logging.getLogger('LotLinx')
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('%s/app.log' % PROJECT_ROOT_PATH)
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

logging.Formatter.converter = time.gmtime
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


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

    url = '%s/%s' % (BASE_URL, _path)
    logger.info("Submitting requests to '%s'." % url)
    resp = r.post(url, json=body, auth=auth)
    logger.info('HTTP response: %s' % resp.content)

    return resp


def check_status(auth, token):
    _path = 'images/%s/status' % token

    url = '%s/%s' % (BASE_URL, _path)
    logger.info("Checking status at '%s'." % url)
    resp = r.get(url, auth=auth)
    logger.info('HTTP response: %s' % resp.content)

    return resp


def load_response(auth, token):
    _path = 'images/%s' % token

    url = '%s/%s' % (BASE_URL, _path)
    logger.info("Loading response from '%s'." % url)
    resp = r.get(url, auth=auth)
    logger.info('HTTP response: %s' % resp.content)

    return resp


if __name__ == '__main__':
    logger.info('Starting solution.\n')

    filename = '%s/inputs/credentials.json' % PROJECT_ROOT_PATH
    credentials = json.load(open(filename))
    auth = HTTPBasicAuth(credentials['username'], credentials['password'])
    logger.info("Credentials loaded from '%s'." % filename)

    filename = '%s/inputs/images.json' % PROJECT_ROOT_PATH
    images = json.load(open(filename))
    logger.info("Images info loaded from '%s'.\n" % filename)

    state = 'SUBMIT_REQUESTS'
    status_code = None
    request_status = None
    token = None
    optimized_images = None
    logger.info('Ready to request.\n')

    while True:
        logger.info('state: %s' % state)

        if state == 'SUBMIT_REQUESTS':
            resp = submit_requests(auth, images)
            status_code = resp.status_code

            state = 'CHECK_STATUS'
            logger.info("State changed to '%s'" % state)

        if state == 'CHECK_STATUS':
            if status_code != 200:
                exception_message = '%s - %s' % (status_code, resp.json()['meta']['errorMsg'])
                logger.error(exception_message)
                raise Exception(exception_message)
            else:
                body = resp.json()['data'][0]
                request_status = body['status']
                token = body['token']

                logger.info('request_status: %s' % request_status)
                logger.info('token: %s' % token)

                if request_status == 'complete':
                    resp = load_response(auth, token)
                    optimized_images = resp.json()['data'][0]['vehicles'][0]['images']
                    break
                elif request_status == 'failed':
                    state = 'SUBMIT_REQUESTS'
                    logger.info("State changed to '%s'" % state)
                elif request_status == 'queued':
                    logger.info('Request queued. Sleeping for a minute.')
                    time.sleep(SLEEP_TIME)
                    resp = check_status(auth, token)

    if optimized_images:
        if not os.path.exists('%s/outputs' % PROJECT_ROOT_PATH):
            os.makedirs('%s/outputs' % PROJECT_ROOT_PATH)

        filename = '%s/outputs/optimized_images.json' % PROJECT_ROOT_PATH
        with open(filename, 'w') as file:
            json.dump(optimized_images, file, indent=4)
            logger.info("Description of optimized images saved in file '%s'." % filename)

        for image in optimized_images:
            image_id = image['imageId']
            modified_url = image['modifiedUrl']

            resp = r.get(modified_url, allow_redirects=True)
            filename = '%s/outputs/optimized_image_%d.png' % (PROJECT_ROOT_PATH, image_id)
            with open(filename, 'wb') as file:
                file.write(resp.content)
                logger.info("Image %d saved in file '%s'." % (image_id, filename))

        logger.info('All images saved.\n')

    logger.info('Finished.')
