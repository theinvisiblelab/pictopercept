# pictopercept

## Requirements
- **Python** >= `3.12.7`
- **node** >= `22.10.0`

## Folder structure
- `app` -> Holds the web/Django's backend code, such as the `views.py` and `urls.py`, that define the routes and what gets shown. Inside also resides the `surveys.json` file.
- `config` -> Where the Django's configuration resides. Won't need much editing probably.
- `static-src` -> Here, all the front-end **SASS** styling and **TypeScript** code resides. When building the project, these files will transpile to pure **CSS** and **JavaScript**, which is needed for browsers.
- `static` -> Holds the static files such as fonts, images, and later the compiled `static-src` files.
- `templates` -> Where all the **HTML** files are located, which are the final web pages that the user will see. They use basic *Django* templating, to pass variables from *Python* to them.

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
python3 manage.py runserver
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
- Run the Python/Django server on port **8000**.

> [!NOTE]
> Your `print` statements might not be visible while using `npm run watch`. To make them visible, use instead of `print`:
> ```python
>  logging.getLogger(__name__).log("Your message goes here.")
> ```


## Building
Make sure you are able to reproduce the [Developing](#developing). Then, once dependencies are installed via `npm install`, you just need to run:
`npm run build`.

## Deploying
TODO
