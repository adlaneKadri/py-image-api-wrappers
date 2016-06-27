import base64
import datetime
import json
import requests
import sys
import os.path
import pprint

GOOGLE_TAG_URL = "https://vision.googleapis.com/v1/images:annotate"


class GoogleVisionApi:

    def __init__(self, api_key):
        self.api_key = api_key
        self.max_num_tags = 30

    def get_image_data(self, image_file_path):
        try:
            return open(image_file_path, 'rb')
        except (IOError, OSError) as e:
            print("Something went wrong! \n" + "Error Message: \n" + str(e))
            return None

    def create_json_request(self, image_data):
        json_request = {'requests': []}
        content_json_obj = {
                'content': base64.b64encode(image_data.read()).decode('UTF-8')
            }
        json_request['requests'].append({"image": content_json_obj, "features": [{"type": "LABEL_DETECTION",
                                                                                 "maxResults": self.max_num_tags}]})
        return json.dumps(json_request)

    def get_tagging_response_and_time(self, image_data):
        try:
            headers = {"Content-Type": "application/json"}
            start_time = datetime.datetime.now()
            response = requests.post(GOOGLE_TAG_URL + "?key=" + self.api_key,
                                     headers=headers, data=self.create_json_request(image_data))
            end_time = datetime.datetime.now()
            return {"response": response, "time": (end_time-start_time).microseconds}
        except requests.exceptions.RequestException as e:
            print("Something went wrong! \n" + "Error Message: \n" + str(e))
            return None

    def get_tag_score_list(self, json_response):
        if not json_response['responses'][0]:
            return []
        response_labels = json_response['responses'][0]['labelAnnotations']
        response_labels_with_score = []
        for label in response_labels:
            response_labels_with_score.append((label["description"], label["score"]))
        return response_labels_with_score

    def parse_response(self, response_and_time):
        status_code = response_and_time["response"].status_code
        if status_code != 200:
            return {"response": json.loads(response_and_time["response"].text), "status": "error"}
        try:
            json_response = json.loads(response_and_time['response'].text)
            tag_list_with_score = self.get_tag_score_list(json_response)
            return {"tag_list": tag_list_with_score, "time": response_and_time['time'], "status": "ok"}
        except KeyError:
            return {"response": json.loads(response_and_time["response"].text), "status": "error"}

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
        print("Wrong number of arguments! \n Usage: python googlevision_api.py <file path to image> <Google Vision API key>")
    else:
        if os.path.isfile(sys.argv[1]):
            googlevision_api = GoogleVisionApi(sys.argv[2])
            pprint.pprint(googlevision_api.get_tag_scores_and_time(sys.argv[1]))
        else:
            print("File not found: " + sys.argv[1])
