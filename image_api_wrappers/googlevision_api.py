import base64
import datetime, json, requests, sys, os.path, pprint

class GoogleVisionApi:

    def __init__(self, api_key):
        self.api_key = api_key
        self.max_num_tags = 30

    def get_tagging_response_and_time(self, image_file_path):
        try:
            tag_url = "https://vision.googleapis.com/v1/images:annotate"
            json_request = {}
            json_request['requests'] = []
            with open(image_file_path, 'rb') as image_file:
                content_json_obj = {
                    'content': base64.b64encode(image_file.read()).decode('UTF-8')
                }
            json_request['requests'].append({"image":content_json_obj, "features": [{"type": "LABEL_DETECTION",
                                                                                     "maxResults": self.max_num_tags}]})
            json_request_string = json.dumps(json_request)
            headers = {"Content-Type": "application/json"}
            start_time = datetime.datetime.now()
            response = requests.post(tag_url +"?key=" + self.api_key,
                                     headers=headers, data=json_request_string)
            end_time = datetime.datetime.now()
            return {"response":response, "time": (end_time-start_time).microseconds}
        except (requests.exceptions.RequestException, FileNotFoundError) as e:
            print("Something went wrong! \n" + "Error Message: \n" +  str(e))
            return

    def get_tag_score_list(self, json_response):
        if json_response['responses'][0]:
            response_labels = json_response['responses'][0]['labelAnnotations']
            response_labels_with_score = []
            for label in response_labels:
                response_labels_with_score.append((label["description"], label["score"]))
            return response_labels_with_score
        else: return []

    def get_tag_score_list_and_time(self, image_file_path):
        response_and_time = self.get_tagging_response_and_time(image_file_path)
        if response_and_time is not None:
            status_code = response_and_time["response"].status_code
            if status_code == 200:
                try:
                    json_response = json.loads(response_and_time['response'].text)
                    tag_list_with_score = self.get_tag_score_list(json_response)
                    return {"tag_list": tag_list_with_score, "time": response_and_time['time'], "status":"ok"}
                except KeyError:
                    return {"message": json.loads(response_and_time["response"].text), "status": "error"}
            elif status_code != 200:
                return {"message": json.loads(response_and_time["response"].text), "status": "error"}


    def get_all_features_response_and_time(self, file_path):
        try:
            json_request = {}
            json_request['requests'] = []
            with open(file_path, 'rb') as image_file:
                content_json_obj = {
                    'content': base64.b64encode(image_file.read()).decode('UTF-8')
                }
            json_request['requests'].append({"image":content_json_obj, "features": [{"type": "LABEL_DETECTION",
                                                                                     "maxResults": self.max_num_tags},
                                                                                    {"type": "LANDMARK_DETECTION",
                                                                                     "maxResults": self.max_num_tags},
                                                                                    {"type": "LOGO_DETECTION",
                                                                                     "maxResults": self.max_num_tags},
                                                                                    {"type": "FACE_DETECTION",
                                                                                     "maxResults": self.max_num_tags}]})
            json_request_string = json.dumps(json_request)
            headers = {"Content-Type": "application/json"}
            start_time = datetime.datetime.now()
            response = requests.post("https://vision.googleapis.com/v1/images:annotate?key=" + self.api_key,
                                     headers=headers, data=json_request_string)
            end_time = datetime.datetime.now()
            return {"response": response, "time": (end_time-start_time).microseconds}
        except (requests.exceptions.RequestException, FileNotFoundError) as e:
            print("Something went wrong! \n" + "Error Message: \n" +  str(e))
            return


if __name__ == '__main__':
    max_num_tags = 30
    if len(sys.argv) < 3:
        print("Too few arguments! \n Usage: python googlevision_api.py <file path to image> <Google Vision API key>")
    if len(sys.argv) >= 3:
        if os.path.isfile(sys.argv[1]):
            googlevision_api = GoogleVisionApi(sys.argv[2], max_num_tags)
            pprint.pprint(googlevision_api.get_tag_score_list_and_time(sys.argv[1]))
        else:
            print("File not found: " + sys.argv[1])