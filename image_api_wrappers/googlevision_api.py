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

    def create_json_request(self, image_file_path):
        json_request = {'requests': []}
        with open(image_file_path, 'rb') as image_file:
            content_json_obj = {
                    'content': base64.b64encode(image_file.read()).decode('UTF-8')
                }
            json_request['requests'].append({"image": content_json_obj, "features": [{"type": "LABEL_DETECTION",
                                                                                     "maxResults": self.max_num_tags}]})
            return json.dumps(json_request)

    def get_tagging_response_and_time(self, image_file_path):
        try:
            headers = {"Content-Type": "application/json"}
            start_time = datetime.datetime.now()
            response = requests.post(GOOGLE_TAG_URL + "?key=" + self.api_key,
                                     headers=headers, data=self.create_json_request(image_file_path))
            end_time = datetime.datetime.now()
            return {"response": response, "time": (end_time-start_time).microseconds}
        except (requests.exceptions.RequestException, FileNotFoundError) as e:
            print("Something went wrong! \n" + "Error Message: \n" + str(e))
            return

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
        if status_code == 200:
            try:
                json_response = json.loads(response_and_time['response'].text)
                tag_list_with_score = self.get_tag_score_list(json_response)
                return {"tag_list": tag_list_with_score, "time": response_and_time['time'], "status": "ok"}
            except KeyError:
                return {"message": json.loads(response_and_time["response"].text), "status": "error"}
        return {"message": json.loads(response_and_time["response"].text), "status": "error"}

    def get_tag_score_list_and_time(self, image_file_path):
        response_and_time = self.get_tagging_response_and_time(image_file_path)
        if response_and_time is not None:
            return self.parse_response(response_and_time)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Too few arguments! \n Usage: python googlevision_api.py <file path to image> <Google Vision API key>")
    if len(sys.argv) >= 3:
        if os.path.isfile(sys.argv[1]):
            googlevision_api = GoogleVisionApi(sys.argv[2])
            pprint.pprint(googlevision_api.get_tag_score_list_and_time(sys.argv[1]))
        else:
            print("File not found: " + sys.argv[1])
