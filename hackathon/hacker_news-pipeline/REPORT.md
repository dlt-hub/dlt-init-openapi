# command line issues

```sh
dlt-init-openapi --help
Usage: dlt-init-openapi [OPTIONS] COMMAND [ARGS]...

  Generate a Python client from an OpenAPI JSON document

Options:
  --version                       Print the version and exit
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.

Commands:
  init  Generate a new OpenAPI Client library
```
I think most the stuff is irrelevant? we should remove completion, no?


```sh
dlt-init-openapi init --help
Usage: dlt-init-openapi init [OPTIONS] [SOURCE]

  Generate a new OpenAPI Client library

Arguments:
  [SOURCE]  A name of data source for which to generate a pipeline

Options:
  --url TEXT                      A URL to read the JSON/YAML spec from
  --path PATH                     A path to the JSON/YAML spec file
  --output-path PATH              A path to render the output to.
  --config PATH                   Path to the config file to use
  --interactive / --no-interactive
                                  Wether to select needed endpoints
                                  interactively  [default: interactive]
  --loglevel INTEGER              Set logging level for stdout output,
                                  defaults to 20 (INFO)  [default: 20]
  --global-limit INTEGER          Set a global limit on the generated source
                                  [default: 0]
  --update-rest-api-source / --no-update-rest-api-source
                                  Wether to update the locally cached rest_api
                                  verified source  [default: no-update-rest-
                                  api-source]
  --help                          Show this message and exit.
```
Does `--update-rest-api-source` really work? what is `global-limit`? Please remove all obsolete arguments.

# hacker news: workflow

`hacker_news_source_original` is the original code

1. I removed data_selector from all endpoints (see bugs below)
2. I converted `items` endpoint into transformer (totally OK, I'd show such thing as part of regular workflow)
3. I added single_page paginator and data_selector explicitly to `items` (see bugs below)

then code ran and dataset is good!

# hacker news: bugs

1. 
```
"endpoint": {
                    "data_selector": "$",
                    "path": "/topstories.json",
                },
```
2024-05-21 14:50:17.163 | WARNING  | dlt_init_openapi:print_warnings:84 - No json response schema defined on main data response. Will not be able to detect primary key and some paginators.

just remove data_selector for autodetect to kick in

2. base url was not set in `config.toml` but it is available:
"swagger": "2.0",
    "info": {
        "title": "Hacker News",
        "description": "<p>Hacker News API</p>\n",
        "version": "1.0.1"
    },
    "host": "hacker-news.firebaseio.com",
    "basePath": "/v0",
    "schemes": [
        "https"
    ],
is this because of swagger 2.0?

3. make module name pythonic:
hacker_news-pipeline -> hacker_news_pipeline
otherwise it is hard to import

4. if paginator is not detected it should be set to "auto" to make the behavior explicit

5. source name coming from CLI is not normalized ie.
```sh
dlt-init-openapi init "hacker | news +" --url https://gist.githubusercontent.com/wing328/44a6cb6c899feda4c2bd44747e9dcbc8/raw/737d3cf34daeef32280c66c5790c7de1a7b26905/hacker_news_api_swagger.json
```
will generate errors during code generation


# improvements to the tool:
- instead of pipeline.py -> hacker_news_pipeline.py
- I'd add progress="log" to dlt.pipeline so people see how it works	
- allow to override the path in which pipeline is created so I can create several pipelines in one place
- [sources] can we be more specific and do [sources.hacker_news] to support many pipelines in a single project?
- any changes to use descriptions of endpoints, params etc. and convert them into comments? could be a flag


# rest client bugfixes and improvements:
- single page entity does not detect {id}.json - bug!
- path should be present in the logs
2024-05-21 15:14:06,614|[INFO                 ]|8151|139916284622656|dlt|client.py|detect_data_selector:259|Detected page data at path: 'kids' type: list length: 7
2024-05-21 15:14:06,619|[INFO                 ]|8151|139916284622656|dlt|client.py|extract_response:240|Extracted data of type list from path kids with length 7

# rest api improvements
- generate @defer for transformers in parallel is on on the resource
- allow DltResource instances in RESTAPIConfig to bring your own custom resources