import datetime, json, requests, sys, os.path, pprint

class ImaggaApi:

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def get_tagging_response_and_time(self, image_file_path):
        try:
            content_url = "https://api.imagga.com/v1/content"
            post_data = {"image": open(image_file_path, 'rb')}
            response = requests.post(content_url, files=post_data, auth=(
            self.api_key, self.api_secret))
            if response.status_code == 200:
                response_json = json.loads(response.text)
                if response_json["status"] == "error":
                    print("Something went wrong! \n" + "Error Message: \n" + response.text)
                    return
                else:
                    image_id = response_json['uploaded'][0]['id']
                    tag_url = "https://api.imagga.com/v1/tagging"
                    post_data = {"content": image_id}
                    start_time = datetime.datetime.now()
                    response = requests.get(tag_url, data=post_data, auth=(
                    self.api_key, self.api_secret))
                    end_time = datetime.datetime.now()
                    return {"response": response, "time": (end_time-start_time).microseconds}
            elif response.status_code != 200:
                print("Something went wrong! \n" + "Error Message: \n" + response.text)
                return
        except (FileNotFoundError, requests.exceptions.RequestException) as e:
            print("Something went wrong! \n" + "Error Message: \n" +  str(e))
            return

    def get_tag_score_list(self, json_response):
        tags = json_response['results'][0]['tags']
        tags_with_confidence = []
        for tag in tags:
            tags_with_confidence.append((tag['tag'], tag['confidence']))
        return tags_with_confidence

    def get_tag_score_list_and_time(self, image_file_path):
        response_and_time = self.get_tagging_response_and_time(image_file_path)
        if response_and_time is not None :
            status_code = response_and_time["response"].status_code
            if status_code == 200:
                json_response = json.loads(response_and_time['response'].text)
                tag_list_with_score = self.get_tag_score_list(json_response)
                return {"tag_list": tag_list_with_score, "time" : response_and_time["time"], "status": "ok"}
            elif status_code != 200:
                return {"status": "error", "message": json.loads(response_and_time["response"].text)}

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Too few arguments! \n Usage: python imagga_api.py <file path to image> <Imagga API key> <Imagga API Secret>")
    if len(sys.argv) >= 4:
        if os.path.isfile(sys.argv[1]):
            imagga_api = ImaggaApi(sys.argv[2], sys.argv[3])
            pprint.pprint(imagga_api.get_tag_score_list_and_time(sys.argv[1]))
        else:
            print("File not found: " + sys.argv[1])