# Converter Server

Server will take download requests from Snapeda website when the downloaded format is OrCAD/Allegro and will start the process to convert an EDF file to an OLB file.

Current implementation:
    Most of the functionalities were just being reused from the azureserver repo. However, I have used class-based views to make it more maintainable and reusable. I have also added comments for further readability.

Since I have no access with the download request url/endpoint of the SnapEDA website, I have created a custom endpoint that will create a job.
    This job will then be added to the queue to process the test zipped file. The test zipped file can be found in the test_resources directory.
    To run the queue for testing, run this command ``python queue_processor.py``. This script will perform requests to get the job that is ready to be processed in the queue. More info on how you test this in the [To Test](#to-test) section

## Requirements

Python 3.x

## Installation
I suggest you to setup a virtual environment of your choice before installing the dependencies.

To install the dependencies of this project, run:
```
pip install -r requirements.txt
```

## Usage (Command Line Execution)
Run Server
```python
python manage.py runserver
```

Run queue processor
```python
python queue_processor.py
```

## To Test
First you need to change the ALLEGRO PATH (line 86) in the batch_extractor.py (inside the processor app) to the path where your allegro application is located. 

You can use Postman to create/simulate requests.
I have added sample requests inside the postman collection (json file in the test_resources directory)

To create a job to be processed, you can post in this endpoint ``http://127.0.0.1:8000/job-queue/``.
This process will create a job that will then be received by the queue processor.

When the queue processor successfully converts the test zipped file, the files will be generated under the test_resources/{name of the zip file}_extracted.

## Endpoints
GET : <host>/job-queue/ -> get jobs to be processed

POST : <host>/job-queue/ -> create jobs for processing

POST : <host>/job-processor/ -> process jobs (endpoint for the conversion of the files located in the zipped file)

## Further Improvements
* Use pywinauto instead of pyautogui to automate application process. The reason for this is that pyautogui uses coordinates (for mouse clicks) that might change due to resolution. This will result to mouse clicking errors if not handled properly. Using pywinauto will be much more efficient since it has functionalities that lets you interact with the elements of the window application. This means that you can directly access an element properly regardless of the resolution of the screen.
