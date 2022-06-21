# How to run this project locally

Please also visit our website at [ZarathusTrust](https://www.zarathustrust.com/)

You will need to have [Python](https://www.python.org/downloads/) installed, as well as [node.js](https://nodejs.org/en/)

Once you have that installed navigate to your desktop and do the following ...

# Clone this repo
* Open up Command Prompt on windows, or Terminal on Mac, then do the following to clone this repository:
```shell script
git clone https://github.com/mohsen-ameli/money-moe-linux.git
```

* navigate to that direcotry
```shell script
cd money-moe-linux
```

* Or you can just download the zip file from the same url listed above and unzip it.

# Backend Setup
<!-- * Install the venv package in order to make a virtual environment
```shell script
python3 -m pip install venv
```

* Then we will use that package to create a new virtual environemt called env
```shell script
python3 -m venv env
```

* Then we will activate that virtual environement
```shell script
source /env/bin/activate
``` -->

* Install all of the required packages
```shell script
python3 -m pip install -r requirements.txt
```

* Get the migrations done.
```shell script
python3 manage.py makemigrations
python3 manage.py migrate
```

* Start the Django server
```shell script
python3 manage.py runserver
```


# Frontend Setup
* Open another terminal window and navigate to the forntend directory:
```shell script
cd frontend
```

* Install all of the required packages for react
```shell script
npm install
```

* Run the react app
```shell script
npm start
```

* navigate to http://localhost:3000

Enjoy :)