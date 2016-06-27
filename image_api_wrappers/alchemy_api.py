import datetime
import json
import requests
import sys
import os.path
import pprint

ALCHEMY_TAG_URL = "https://gateway-a.watsonplatform.net/calls/image/ImageGetRankedImageKeywords"


class AlchemyApi:

    def __init__(self, api_key):
        self.api_key = api_key

    def get_image_data(self, image_file_path):
        try:
            image_data = open(image_file_path, 'rb').read()
            return image_data
        except (OSError, IOError) as e:
            print("Something went wrong! \n" + "Error Message: \n" + str(e))
            return None

    def get_tagging_response_and_time(self, image_data):
        try:
            start_time = datetime.datetime.now()
            response = requests.post(ALCHEMY_TAG_URL + "?apikey=" +
                                     self.api_key + "&outputMode=json&imagePostMode=raw",
                                     data=image_data)
            end_time = datetime.datetime.now()
            return {"response": response, "time": (end_time-start_time).microseconds}
        except requests.exceptions.RequestException as e:
            print("Something went wrong! \n" + "Error Message: \n" + str(e))
            return None

    def get_tag_score_list(self, json_response):
        return [(tag['text'], tag['score']) for tag in json_response['imageKeywords']
                if tag['text'] != 'NO_TAGS']

    def parse_response(self, response_and_time):
        status_code = response_and_time["response"].status_code
        json_response = json.loads(response_and_time['response'].text)
        if status_code != 200 or json_response["status"] == "ERROR":
            return {"response": json.loads(response_and_time["response"].text), "status": "error"}
        tag_list_with_score = self.get_tag_score_list(json_response)
        return {"tag_list": tag_list_with_score, "time": response_and_time['time'], "status": "ok"}

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
        print("Wrong number of arguments! \n Usage: python alchemy_api.py <file path to image> <Alchemy API key>")
    else:
        if os.path.isfile(sys.argv[1]):
            alchemy_api = AlchemyApi(sys.argv[2])
            pprint.pprint(alchemy_api.get_tag_scores_and_time(sys.argv[1]))
        else:
            print("File not found: " + sys.argv[1])
