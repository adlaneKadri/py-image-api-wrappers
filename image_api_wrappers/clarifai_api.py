import datetime, json, requests, sys, os.path, pprint

class ClarifaiApi:

    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.clarifai_access_token = None
        self.base_url = "https://api.clarifai.com/v1/"

    def get_token(self):
        token_url = "token/"
        post_data = {"client_id" : self.app_id, "client_secret": self.app_secret, "grant_type": "client_credentials"}
        try:
            response = requests.post(self.base_url + token_url, data=post_data)
            if response.status_code == 200:
                json_response = json.loads(response.text)
                return json_response["access_token"]
            elif response.status_code != 200:
                print("Something went wrong! \n" + "Error Message: \n" + response.text)
                return
        except requests.exceptions.RequestException as e:
            print("Something went wrong! \n" + "Error Message: \n" +  str(e))
            return

    def get_tagging_response_and_time(self, file_path):
        try:
            tag_url = "tag/"
            if self.clarifai_access_token is None:
                self.clarifai_access_token = self.get_token()
                if self.clarifai_access_token is None: return
            post_data = {"encoded_data": open(file_path, 'rb')}
            headers = {"Authorization": "Bearer " + self.clarifai_access_token}
            start_time = datetime.datetime.now()
            response = requests.post(self.base_url + tag_url, headers=headers, files=post_data)
            end_time = datetime.datetime.now()
            return {"response":response, "time": (end_time-start_time).microseconds}
        except (requests.exceptions.RequestException, FileNotFoundError, TypeError) as e:
            print("Something went wrong! Exiting. \n" + "Error Message: \n" +  str(e))
            return

    def get_tag_score_list(self, json_response):
        tag_list =  json_response['results'][0]['result']['tag']['classes']
        prob_list = json_response['results'][0]['result']['tag']['probs']
        return (list(zip(tag_list, prob_list)))

    def get_tag_score_list_and_time(self, image_file_path):
        response_and_time = self.get_tagging_response_and_time(image_file_path)
        if response_and_time is not None:
            status_code = response_and_time["response"].status_code
            if status_code == 200:
                json_response = json.loads(response_and_time['response'].text)
                tag_list_with_score = self.get_tag_score_list(json_response)
                return {"tag_list": tag_list_with_score, "time": response_and_time['time'], "status": "ok"}
            elif status_code != 200:
                return {"message": json.loads(response_and_time["response"].text), "status": "error"}


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Too few arguments! \n Usage: python clarifai_api.py <file path to image> <Clarifai app id> <Clarifai app secret>")
    if len(sys.argv) >= 4:
        if os.path.isfile(sys.argv[1]):
            clarifai_api = ClarifaiApi(sys.argv[2], sys.argv[3])
            pprint.pprint(clarifai_api.get_tag_score_list_and_time(sys.argv[1]))
        else:
            print("File not found: " + sys.argv[1])