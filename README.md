# Python API wrappers for Image Content Tagging
## Google Vision API, Clarifai, Imagga, Projectoxford and Alchemy API

This repository contains basic API-wrappers for the image tagging function for some of the biggest Image recognition and object detection API:s out there atm.

## Requirements
Python 3+

## Installation
Installation is necessary if you are going to use it as a module. 
```
python setup.py install
```

## Usage

There are two possible usages for the library. Either from the command-line or as an imported module in python. 
All wrappers have one common function to run to get the image content tags: get_tag_score_list_and_time("<file path to image>")

### Clarifai API
[Clarifai website](https://www.clarifai.com/)  
Command line use: 
```
python clarifai_api <file path to image> <Clarifai app id> <Clarifai app secret>
```

Module use: 
```
from image_api_wrappers import clarifai_api

clarifai_wrapper = clarifai_api.ClarifaiApi("<Clarifai app id>", "<Clarifai app secret>")

clarifai_wrapper.get_tag_score_list_and_time("<file path to image>")
```

### Imagga API
[Imagga website](http://imagga.com/)  
Command line use: 
```
python imagga_api <file path to image> <Imagga API key> <Imagga API Secret>
```

Module use: 
```
from image_api_wrappers import imagga_api

imagga_wrapper = imagga_api.ImaggaApi("<Imagga API key>", "<Imagga API Secret>")

imagga_wrapper.get_tag_score_list_and_time("<file path to image>")
```

### Alchemy API
[Alchemy website](http://www.alchemyapi.com/)  
Command line use: 
```
python alchemy_api <file path to image> <Alchemy API key>
```

Module use: 
```
from image_api_wrappers import alchemy_api

alchemy_wrapper = imagga_api.AlchemyApi("<Alchemy API key>")

alchemy_wrapper.get_tag_score_list_and_time("<file path to image>")
```

### Google Vision API
[Google Vision API website](https://cloud.google.com/vision/)  
Command line use: 
```
python googlevision_api <file path to image> <Google Vision API key>
```

Module use: 
```
from image_api_wrappers import googlevision_api

googlevision_wrapper = googlevision_api.GoogleVisionApi("<Google Vision API key>")

googlevision_wrapper.get_tag_score_list_and_time("<file path to image>")
```

### Projectoxford API
[Projectoxford API website](https://www.microsoft.com/cognitive-services/en-us/computer-vision-api)  
Command line use: 
```
python projectoxford_api <file path to image> <Projectoxford API key>
```

Module use: 
```
from image_api_wrappers import projectoxford_api

projectoxford_wrapper = projectoxford_api.ProjectoxfordApi("<Projectoxford API key>")

projectoxford_wrapper.get_tag_score_list_and_time("<file path to image>")
```

### Return values 
#### OK Response
{
    "status" : "ok", 
    "tag_list" : < A list of tuples with each tag and their respective confidence values >, 
    "time" : "< The response time in micro seconds >"
}

#### Error Response
{
    "status": "error", 
    "message": "< The returned message from the API >".
}

#### Internal Error
If an internal error occurs the error will be printed and the function get_tag_score_list_and_time("< file path to image >") will return None. 

## Example Usage
The example image used is from the PASCAL-VOC 2007 test data set. 
Example usage when running in command line: 
```
python clarifai_api.py ../img/cats.jpg <Clarifai app id> <Clarifai app secret>
```
Output is a dictionary mapping "tag_list" to all tags and confidences and mappin "time" to the response ime in micro seconds.  
```
{'tag_list': [('mammal', 0.9875457286834717),
              ('cat', 0.9859105944633484),
              ('animal', 0.9846997857093811),
              ('cute', 0.9829119443893433),
              ('pet', 0.9789081811904907),
              ('portrait', 0.9677218198776245),
              ('domestic', 0.960905909538269),
              ('fur', 0.957800567150116),
              ('grass', 0.9479244351387024),
              ('young', 0.933842122554779),
              ('kitten', 0.9197168350219727),
              ('nature', 0.9172214269638062),
              ('little', 0.9138644933700562),
              ('eye', 0.9093579649925232),
              ('looking', 0.9006421566009521),
              ('adorable', 0.9006125330924988),
              ('one', 0.8975734710693359),
              ('no person', 0.8964280486106873),
              ('baby', 0.88373863697052),
              ('funny', 0.8553003072738647)],
 'time': 295135}
```

## License
MIT
