import datetime, json, requests, sys, os.path, pprint

class ProjectoxfordApi:

    def __init__(self, api_key):
        self.api_key = api_key

    def get_tagging_response_and_time(self, image_file_path):
        try:
            tag_url = "https://api.projectoxford.ai/vision/v1.0/tag"
            data = open(image_file_path, 'rb')
            headers = {'Content-Type': 'application/octet-stream', 'Ocp-Apim-Subscription-Key': self.api_key}
            start_time = datetime.datetime.now()
            response = requests.post(tag_url, data=data, headers=headers)
            end_time = datetime.datetime.now()
            return {"response": response, "time": (end_time-start_time).microseconds}
        except (requests.exceptions.RequestException, FileNotFoundError) as e:
            print("Something went wrong! \n" + "Error Message: \n" +  str(e))
            return

    def get_tag_score_list(self, json_response):
        tags = json_response['tags']
        tags_with_confidence = []
        for tag in tags:
            tags_with_confidence.append((tag['name'], tag['confidence']))
        return tags_with_confidence

    def get_tag_score_list_and_time(self, image_file_path):
        response_and_time = self.get_tagging_response_and_time(image_file_path)
        if response_and_time is not None :
            status_code = response_and_time["response"].status_code
            if status_code == 200:
                json_response = json.loads(response_and_time['response'].text)
                tag_list_with_score = self.get_tag_score_list(json_response)
                return {"tag_list": tag_list_with_score, "time" : response_and_time["time"], "status":"ok"}
            elif status_code != 200:
                return {"message": json.loads(response_and_time["response"].text), "status":"error"}

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Too few arguments! \n Usage: python projectoxford_api.py <file path to image> <Projectoxford API key>")
    if len(sys.argv) >= 2:
        if os.path.isfile(sys.argv[1]):
            projectoxford_api = ProjectoxfordApi(sys.argv[2])
            pprint.pprint(projectoxford_api.get_tag_score_list_and_time(sys.argv[1]))
        else:
            print("File not found: " + sys.argv[1])
