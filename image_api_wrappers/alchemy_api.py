import datetime, json, requests, sys, os.path, pprint

class AlchemyApi:

    def __init__(self, api_key):
        self.api_key = api_key

    def get_tagging_response_and_time(self, image_file_path):
        tag_url = "https://gateway-a.watsonplatform.net/calls/image/ImageGetRankedImageKeywords"
        try:
            start_time = datetime.datetime.now()
            response = requests.post(tag_url + "?apikey="
                                     + self.api_key + "&outputMode=json&imagePostMode=raw",
                                     data=open(image_file_path, 'rb').read())
            end_time = datetime.datetime.now()
            json_response = json.loads(response.text)
            if json_response["status"] == "ERROR":
                print("Something went wrong! \n" + "Error Message: \n" +  response.text)
                return
            else:
                return {"response": response, "time": (end_time-start_time).microseconds}
        except (requests.exceptions.RequestException, FileNotFoundError) as e:
            print("Something went wrong! \n" + "Error Message: \n" +  str(e))
            return

    def get_tag_score_list(self, json_response):
        tag_list = json_response["imageKeywords"]
        tag_list_with_score = []
        for tag in tag_list:
            if tag['text'] == 'NO_TAGS': break
            tag_list_with_score.append((tag['text'], tag['score']))
        return tag_list_with_score

    def get_tag_score_list_and_time(self, image_file_path):
        response_and_time = self.get_tagging_response_and_time(image_file_path)
        if response_and_time is not None :
            status_code = response_and_time["response"].status_code
            if status_code == 200:
                json_response = json.loads(response_and_time['response'].text)
                tag_list_with_score = self.get_tag_score_list(json_response)
                return {"tag_list": tag_list_with_score, "time": response_and_time['time'], "status": "ok"}
            elif status_code != 200:
                return {"message": json.loads(response_and_time["response"].text), "status" : "error"}

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Too few arguments! \n Usage: python alchemy_api.py <file path to image> <Alchemy API key>")
    if len(sys.argv) >= 2:
        if os.path.isfile(sys.argv[1]):
            alchemy_api = AlchemyApi(sys.argv[2])
            pprint.pprint(alchemy_api.get_tag_score_list_and_time(sys.argv[1]))
        else:
            print("File not found: " + sys.argv[1])