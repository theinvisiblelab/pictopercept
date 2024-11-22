# pictopercept

## Requirements
- **Python** >= `3.11.4`
- **node** >= `22.11.0`

## Project structure
- `pictopercept` -> Holds the web/Flask's python backend code, such as the `views.py` and `urls.py`, that define the routes and what gets shown. Inside also resides the `surveys.json` file.
- `pictopercept/templates` -> Where all the **HTML** files are located, which are the final web pages that the user will see. They use basic *Flask/Jinja2* templating, to pass variables from *Python* to them.
- `pictopercept/static` -> Holds the static files such as fonts, images, and later the compiled `static-src` files.
- `pictopercept/surveys.json` -> Where the active survey list reside. Check the structure inside `pictopercept/survey.py` python class. (currently, the default one is `jobs` survey, but this can be easily changed to point via url in the future (e.g. `pictopercept.ai/survey/<survey-id>`).
- `static-src` -> Here, all the front-end **SASS** styling and **TypeScript** code resides. When building the project, these files will transpile to pure **CSS** and **JavaScript**, which is needed for browsers.

## Developing
Install the tools defined in [requirements](#requirements).
### Python environment
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
To manually run the server, you can run:
```
flask run --debug
```
but it is recommended to execute it via `npm run watch` command, which it's explained in the following section, [Npm/Node-basic-setup](#npmnode-basic-setup)

### Npm/node basic setup
Then, while being at the project root, the first time you should run:
```
npm install
```
Which will install all the node-related dependencies (that is, the needed libraries to transpile the `static` files).

Then, you just need to run:
```
npm run watch
```
This command will:
- Transpile on each `static-src` file change all the **SASS** and **TypeScript** code into the `static` folder.
- Run the Python/Flask server on port **5000**, in **Debug** mode.

> [!NOTE]
> Your `print` statements might not be visible while using `npm run watch`. To make them visible, use the logger instead of `print`:
> ```python
>  logging.getLogger(__name__).debug("Your message goes here."); # .debug(), .warning(), .error() and .critical() are other alternatives.
> ```
> or just execute the server manually via `flask run` command, which would also output `print` statements.


## Building
Make sure you are able to reproduce the [Developing](#developing). Then, once dependencies are installed via `npm install`, you just need to run:
`npm run build`.

## Dockerfile
## Dockerfile/Deploying
TBD

You need to pass the environment variable `MONGODB_URI` when running the image.
