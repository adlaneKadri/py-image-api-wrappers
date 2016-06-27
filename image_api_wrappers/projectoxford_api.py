import datetime
import json
import requests
import sys
import os.path
import pprint

PROJECTOXFORD_TAG_URL = "https://api.projectoxford.ai/vision/v1.0/tag"


class ProjectoxfordApi:

    def __init__(self, api_key):
        self.api_key = api_key

    def get_image_data(self, image_file_path):
        try:
            return open(image_file_path, 'rb')
        except (IOError, OSError) as e:
            print("Something went wrong! \n" + "Error Message: \n" + str(e))
            return None

    def get_tagging_response_and_time(self, image_data):
        try:
            headers = {'Content-Type': 'application/octet-stream', 'Ocp-Apim-Subscription-Key': self.api_key}
            start_time = datetime.datetime.now()
            response = requests.post(PROJECTOXFORD_TAG_URL, data=image_data, headers=headers)
            end_time = datetime.datetime.now()
            return {"response": response, "time": (end_time-start_time).microseconds}
        except requests.exceptions.RequestException as e:
            print("Something went wrong! \n" + "Error Message: \n" + str(e))
            return None

    def get_tag_score_list(self, json_response):
        return [(tag['name'], tag['confidence']) for tag in json_response['tags']]

    def parse_response(self, response_and_time):
        status_code = response_and_time["response"].status_code
        if status_code != 200:
            return {"response": json.loads(response_and_time["response"].text), "status": "error"}
        json_response = json.loads(response_and_time['response'].text)
        tag_list_with_score = self.get_tag_score_list(json_response)
        return {"tag_list": tag_list_with_score, "time": response_and_time["time"], "status": "ok"}

    def get_tag_scores_and_time(self, image_file_path):
        image_data = self.get_image_data(image_file_path)
        if image_data is None:
            return None
        response_and_time = self.get_tagging_response_and_time(image_data)
        if response_and_time is None:
            return None
        return self.parse_response(response_and_time)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Wrong number of arguments! \n Usage: python projectoxford_api.py <file path to image> <Projectoxford API key>")
    else:
        if os.path.isfile(sys.argv[1]):
            projectoxford_api = ProjectoxfordApi(sys.argv[2])
            pprint.pprint(projectoxford_api.get_tag_scores_and_time(sys.argv[1]))
        else:
            print("File not found: " + sys.argv[1])
