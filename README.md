# zoomapp---backend-fastapi


### Create .env from .env.sample to have the following variables
```
ZOOM_WEBHOOK_SECRET_TOKEN=****
ZOOM_API_KEY=****
ZOOM_API_SECRET=****
```


### Create the environment
```
python3 -m venv venv
```


### If you are using windows, run the following command
```
.\venv\Scripts\activate
```


### Or If you are using Mac or Linux, run the following command
```
source venv/bin/activate
```


### And then install the packages for the project via pip
```
pip install -r requirements.txt
```


### Finally the run the project
```
python main.py
```