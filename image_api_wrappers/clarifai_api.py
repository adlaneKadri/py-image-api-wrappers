import datetime
import json
import requests
import sys
import os.path
import pprint

CLARIFAI_BASE_URL = "https://api.clarifai.com/v1/"
CLARIFAI_TAG_URL = "tag/"
CLARIFAI_TOKEN_URL = "token/"

class ClarifaiApi:

    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.clarifai_access_token = None

    def fetch_token_response(self):
        post_data = {"client_id": self.app_id, "client_secret": self.app_secret, "grant_type": "client_credentials"}
        try:
            return requests.post(CLARIFAI_BASE_URL + CLARIFAI_TOKEN_URL, data=post_data)
        except requests.exceptions.RequestException as e:
            print("Something went wrong! \n" + "Error Message: \n" + str(e))
            return None

    def set_token(self):
        token_response = self.fetch_token_response()
        if token_response.status_code != 200:
            return {"response": token_response.text, "status": "error"}
        json_response = json.loads(token_response.text)
        self.clarifai_access_token =  json_response["access_token"]
        return {"status": "ok"}

    def get_image_data(self, image_file_path):
        try:
            return open(image_file_path, 'rb')
        except (OSError, IOError) as e:
            print("Something went wrong! \n" + "Error Message: \n" + str(e))
            return None

    def get_tagging_response_and_time(self, image_data):
        try:
            post_data = {"encoded_data": image_data}
            headers = {"Authorization": "Bearer " + self.clarifai_access_token}
            start_time = datetime.datetime.now()
            response = requests.post(CLARIFAI_BASE_URL + CLARIFAI_TAG_URL, headers=headers, files=post_data)
            end_time = datetime.datetime.now()
            return {"response": response, "time": (end_time-start_time).microseconds}
        except requests.exceptions.RequestException as e:
            print("Something went wrong! Exiting. \n" + "Error Message: \n" + str(e))
            return None

    def get_tag_score_list(self, json_response):
        tag_list = json_response['results'][0]['result']['tag']['classes']
        prob_list = json_response['results'][0]['result']['tag']['probs']
        return list(zip(tag_list, prob_list))

    def parse_response(self, response_and_time):
        status_code = response_and_time["response"].status_code
        if status_code != 200:
            return {"response": json.loads(response_and_time["response"].text), "status": "error"}
        json_response = json.loads(response_and_time['response'].text)
        tag_list_with_score = self.get_tag_score_list(json_response)
        return {"tag_list": tag_list_with_score, "time": response_and_time['time'], "status": "ok"}

    def get_tag_scores_and_time(self, image_file_path):
        if self.clarifai_access_token is None:
            token_status = self.set_token()
            if token_status["status"] == "error":
                return token_status
        image_data = self.get_image_data(image_file_path)
        if image_data is None:
            return None
        response_and_time = self.get_tagging_response_and_time(image_data)
        if response_and_time is None:
            return None
        return self.parse_response(response_and_time)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Wrong number of arguments! \n Usage: python clarifai_api.py <file path to image> <Clarifai app id> "
              "<Clarifai app secret>")
    else:
        if os.path.isfile(sys.argv[1]):
            clarifai_api = ClarifaiApi(sys.argv[2], sys.argv[3])
            pprint.pprint(clarifai_api.get_tag_scores_and_time(sys.argv[1]))
        else:
            print("File not found: " + sys.argv[1])
