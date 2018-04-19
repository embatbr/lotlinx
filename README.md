# LotLinx

This directory is also a git repository. See the hidden directory and file *.git* and *.gitignore*.

The project was written using Ubuntu 16.04.

## Requirements

- Python 3.5 (I cannot guarantee a previous version will execute correctly).
- Modules `json`, `os`, `requests`, `time`, all provided by the Python installation.

## Execution

- Provide a JSON file *credentials.json* inside directory *inputs* with fields `username` and `password` filled with the correct data.
- Run the bash file *startup.sh*.

## Problem description

Given the provided URLs to images of vehicles and the API documentation please construct a request to submit the images to the API using the credentials given, poll for job completion and get the results from the finished job.

The Image API classifies images, provides coordinates of a box that surrounds the primary vehicle in the image and enhances the image by blurring the background to highlight the primary vehicle.

- [X] Use PHP, Python or Java to implement your solution.
- [X] Basic error handling should be implemented, but no heroics necessary.
- [X] The program should take the Image URLs as input, as parameters, stdin, read from file, etc.
- [X] API responses should be logged
- [ ] Provide a ZIP/archive of the program code, logged output and resulting images downloaded from the API results.

Here are the image URLS:

https://img.lotlinx.com/vdn/7416/jeep_wrangler%20unlimited_2014_1C4BJWFG3EL326863_7416_339187295.jpg
https://img.lotlinx.com/vdn/7416/jeep_wrangler%20unlimited_2014_1C4BJWFG3EL326863_7416_2_339187295.jpg
https://img.lotlinx.com/vdn/7416/jeep_wrangler%20unlimited_2014_1C4BJWFG3EL326863_7416_3_339187295.jpg
https://img.lotlinx.com/vdn/7416/jeep_wrangler%20unlimited_2014_1C4BJWFG3EL326863_7416_4_339187295.jpg
https://img.lotlinx.com/vdn/7416/jeep_wrangler%20unlimited_2014_1C4BJWFG3EL326863_7416_5_339187295.jpg

