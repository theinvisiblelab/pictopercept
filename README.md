# 📷 PictoPercept

PictoPercept is a fully open-source survey toolkit designed to study human and machine preferences in an increasingly digitized world. PictoPercept provides visual choice scenarios, where one can make choices by comparing pairs of facial images in short time frames. You can try out sample surveys [here](https://pictopercept.ai/).

**🌱 Supported By**

- Amsterdam School of Communication Research, University of Amsterdam
- Digital Communication Methods Lab, University of Amsterdam 
 
Reach out to [saurabh.khanna@uva.nl](mailto:saurabh.khanna@uva.nl) with feedback and/or questions.

## Project structure

- `pictopercept` -> Holds the web/Flask's python backend code, such as the `views.py` and `db.py`, that define the routes and what gets shown.
- `pictopercept/templates` -> Where all the **HTML** files are located, which are the final web pages that the user will see. They use basic *Flask/Jinja2* templating, to pass variables from *Python* to them.
- `pictopercept/static` -> Holds the static files such as `JavaScript` and `CSS` code, fonts and images.
- `pictopercept/lib` -> A custom library that defines custom types and default survey handlers to make defining new surveys easier.
- `pictopercept/surveys` -> Here is where you should place all the custom surveys to show in the website. You can view the base survey definition at `pictopercept/lib/common_types.py` to view all the needed attributes and functions to implement per survey.

## Developing

First, make sure to check [Environment Variables](#environment-variables) and [Storage and Database](#storage-and-database) to setup everything properly.

It is recommended to use some sort of virtual environment, such as `venv` (there are other alternatives such as *pipenv* or *conda*), which will help get and manage the correct versions of python-related libraries:
```
python3 -m venv .venv
```
Then, to activate the environment:
```
source .venv/bin/activate
```
Once done, you can execute the following to install all the python dependencies:
```
pip3 install -r requirements.txt
```
Then, run the server using:
```
flask run --debug
```
This command will start the local website in the port 5000. You can visit [http://localhost:5000](http://localhost:5000) in your browser to view it.

## Environment Variables

There is a provided `.env.example` where you can view all the env variables used by our program.

These are:
- `FLASK_SECRET_KEY`: A random hex key that Flask will use to encrypt session data into the cookies.
- `FETCH_PASSWORD`: A random hex key to use that is needed to fetch all the survey data (such as user answers).
- `MONGODB_URI`, `DATABASE_PATH` and `DATASETS_PATH`: Please check [Storage and Database](#storage-and-database)

## Storage and Database

### Deployed on Surf SRAM

When Pictopercept is deployed in **SURF SRAM**, it uses two attached storages named `db` and `pictopercept_datasets`, which are attached in the server's `/data/db/` and `/data/pictopercept_datasets/`, respectively.
It will also use the `mongo` service that is defined in the [docker-compose.yml](./docker-compose.yml) file.

Because of this, the ENV used by the deployment (appart from the secret keys) will just be:
- `MONGODB_URI`: `mongo:27017`
- `DATABASE_PATH`: `/data/db`
- `DATASETS_PATH`: `/data/pictopercept_datasets`

### Developing locally

#### Database

When developing Pictopercept locally, we need some extra external services such as MongoDB running and a dataset folder. There are two recommended options:

##### In memory via `mongomock` (non-persistent)

You can also pass the flag `-debug` when opening the server (via `flask run --debug`) to use the in-memory database. However, this is not persistent, and MongoDB mock service will restart on each `flask` run/update.

##### MongoDB using Docker service (persistent locally)

One easy way would just be using the Docker Compose service's MongoDB locally. To do this, you can run it and just set the `MONGODB_URI` to `mongodb://localhost:27017/`.

#### Database and Dataset folders
You will need to create two folders wherever you want and point both envs to those folders (`DATABASE_PATH` and `DATASETS_PATH`).
