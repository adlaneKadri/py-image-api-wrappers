import datetime
import json
import requests
import sys
import os.path
import pprint

IMAGGA_CONTENT_URL = "https://api.imagga.com/v1/content"
IMAGGA_TAG_URL = "https://api.imagga.com/v1/tagging"


class ImaggaApi:

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def get_image_data(self, image_file_path):
        try:
            return open(image_file_path, 'rb')
        except (IOError, OSError) as e:
            print("Something went wrong! \n" + "Error Message: \n" + str(e))
            return None

    def get_image_response(self, response):
        response_json = json.loads(response.text)
        if response_json["status"] == "error":
            print("Something went wrong! \n" + "Error Message: \n" + response.text)
            return None
        image_id = response_json['uploaded'][0]['id']
        post_data = {"content": image_id}
        start_time = datetime.datetime.now()
        response = requests.get(IMAGGA_TAG_URL, data=post_data, auth=(self.api_key, self.api_secret))
        end_time = datetime.datetime.now()
        return {"response": response, "time": (end_time-start_time).microseconds}

    def get_tagging_response_and_time(self, image_data):
        try:
            post_data = {"image": image_data}
            response = requests.post(IMAGGA_CONTENT_URL, files=post_data, auth=(self.api_key, self.api_secret))
            if response.status_code != 200:
                return {"response": response}
            return self.get_image_response(response)
        except requests.exceptions.RequestException as e:
            print("Something went wrong! \n" + "Error Message: \n" + str(e))
            return None

    def get_tag_score_list(self, json_response):
        tags = json_response['results'][0]['tags']
        tags_with_confidence = []
        for tag in tags:
            tags_with_confidence.append((tag['tag'], tag['confidence']))
        return tags_with_confidence

    def parse_response(self, response_and_time):
        status_code = response_and_time["response"].status_code
        if status_code != 200:
            return {"status": "error", "response": json.loads(response_and_time["response"].text)}
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
    if len(sys.argv) != 4:
        print("Wrong number of arguments! \n Usage: python imagga_api.py <file path to image> <Imagga API key> "
              "<Imagga API Secret>")
    else:
        if os.path.isfile(sys.argv[1]):
            imagga_api = ImaggaApi(sys.argv[2], sys.argv[3])
            pprint.pprint(imagga_api.get_tag_scores_and_time(sys.argv[1]))
        else:
            print("File not found: " + sys.argv[1])
