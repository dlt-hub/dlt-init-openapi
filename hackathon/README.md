# Google BigQuery source

## Feedback

### Pipeline didn't run
I couldn't figure out where I should be passing the access token. The generated config had "access_token" as a parameter, but pasting the token here didn't work.

Stack trace:
```
2024-05-22 14:15:57,304|[INFO                 ]|8304|15720|dlt|pipeline.py|_restore_state_from_destination:1414|The state was restored from the destination duckdb(dlt.destinations.duckdb):google_bigquery_data
2024-05-22 14:15:57,360|[INFO                 ]|8304|15720|dlt|client.py|_send_request:128|Making GET request to https://bigquery.googleapis.com/bigquery/v2/projects with params={'pageToken': 0}, json=None

Traceback (most recent call last):
  File "C:\Users\rahul\OneDrive\Desktop\Work\openapi_hackathon\dlt-init-openapi\env\lib\site-packages\dlt\extract\pipe_iterator.py", line 275, in _get_source_item
    pipe_item = next(gen)
  File "C:\Users\rahul\OneDrive\Desktop\Work\openapi_hackathon\dlt-init-openapi\hackathon\google_bigquery-pipeline\rest_api\__init__.py", line 263, in paginate_resource
    yield from client.paginate(
  File "C:\Users\rahul\OneDrive\Desktop\Work\openapi_hackathon\dlt-init-openapi\env\lib\site-packages\dlt\sources\helpers\rest_client\client.py", line 211, in paginate
    response = self._send_request(request)
  File "C:\Users\rahul\OneDrive\Desktop\Work\openapi_hackathon\dlt-init-openapi\env\lib\site-packages\dlt\sources\helpers\rest_client\client.py", line 135, in _send_request
    return self.session.send(prepared_request)
  File "C:\Users\rahul\OneDrive\Desktop\Work\openapi_hackathon\dlt-init-openapi\env\lib\site-packages\requests\sessions.py", line 710, in send        
    r = dispatch_hook("response", hooks, r, **kwargs)
  File "C:\Users\rahul\OneDrive\Desktop\Work\openapi_hackathon\dlt-init-openapi\env\lib\site-packages\requests\hooks.py", line 30, in dispatch_hook   
    _hook_data = hook(hook_data, **kwargs)
  File "C:\Users\rahul\OneDrive\Desktop\Work\openapi_hackathon\dlt-init-openapi\env\lib\site-packages\dlt\sources\helpers\rest_client\client.py", line 197, in raise_for_status
    response.raise_for_status()
  File "C:\Users\rahul\OneDrive\Desktop\Work\openapi_hackathon\dlt-init-openapi\env\lib\site-packages\requests\models.py", line 1024, in raise_for_status
    raise HTTPError(http_error_msg, response=self)
requests.exceptions.HTTPError: 401 Client Error: Unauthorized for url: https://bigquery.googleapis.com/bigquery/v2/projects?pageToken=0

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\rahul\OneDrive\Desktop\Work\openapi_hackathon\dlt-init-openapi\env\lib\site-packages\dlt\pipeline\pipeline.py", line 431, in extract 
    self._extract_source(extract_step, source, max_parallel_items, workers)
  File "C:\Users\rahul\OneDrive\Desktop\Work\openapi_hackathon\dlt-init-openapi\env\lib\site-packages\dlt\pipeline\pipeline.py", line 1105, in _extract_source
    load_id = extract.extract(source, max_parallel_items, workers)
  File "C:\Users\rahul\OneDrive\Desktop\Work\openapi_hackathon\dlt-init-openapi\env\lib\site-packages\dlt\extract\extract.py", line 397, in extract   
    self._extract_single_source(
  File "C:\Users\rahul\OneDrive\Desktop\Work\openapi_hackathon\dlt-init-openapi\env\lib\site-packages\dlt\extract\extract.py", line 326, in _extract_single_source
    for pipe_item in pipes:
  File "C:\Users\rahul\OneDrive\Desktop\Work\openapi_hackathon\dlt-init-openapi\env\lib\site-packages\dlt\extract\pipe_iterator.py", line 159, in __next__
    pipe_item = self._get_source_item()
  File "C:\Users\rahul\OneDrive\Desktop\Work\openapi_hackathon\dlt-init-openapi\env\lib\site-packages\dlt\extract\pipe_iterator.py", line 306, in _get_source_item
    raise ResourceExtractionError(pipe.name, gen, str(ex), "generator") from ex
dlt.extract.exceptions.ResourceExtractionError: In processing pipe bigquery_projects_list: extraction of resource bigquery_projects_list in generator paginate_resource caused an exception: 401 Client Error: Unauthorized for url: https://bigquery.googleapis.com/bigquery/v2/projects?pageToken=0       

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\rahul\OneDrive\Desktop\Work\openapi_hackathon\dlt-init-openapi\hackathon\google_bigquery-pipeline\pipeline.py", line 15, in <module> 
    info = pipeline.run(source)
  File "C:\Users\rahul\OneDrive\Desktop\Work\openapi_hackathon\dlt-init-openapi\env\lib\site-packages\dlt\pipeline\pipeline.py", line 222, in _wrap   
    step_info = f(self, *args, **kwargs)
  File "C:\Users\rahul\OneDrive\Desktop\Work\openapi_hackathon\dlt-init-openapi\env\lib\site-packages\dlt\pipeline\pipeline.py", line 267, in _wrap   
    return f(self, *args, **kwargs)
  File "C:\Users\rahul\OneDrive\Desktop\Work\openapi_hackathon\dlt-init-openapi\env\lib\site-packages\dlt\pipeline\pipeline.py", line 673, in run     
    self.extract(
  File "C:\Users\rahul\OneDrive\Desktop\Work\openapi_hackathon\dlt-init-openapi\env\lib\site-packages\dlt\pipeline\pipeline.py", line 222, in _wrap   
    step_info = f(self, *args, **kwargs)
  File "C:\Users\rahul\OneDrive\Desktop\Work\openapi_hackathon\dlt-init-openapi\env\lib\site-packages\dlt\pipeline\pipeline.py", line 176, in _wrap   
    rv = f(self, *args, **kwargs)
  File "C:\Users\rahul\OneDrive\Desktop\Work\openapi_hackathon\dlt-init-openapi\env\lib\site-packages\dlt\pipeline\pipeline.py", line 162, in _wrap   
    return f(self, *args, **kwargs)
  File "C:\Users\rahul\OneDrive\Desktop\Work\openapi_hackathon\dlt-init-openapi\env\lib\site-packages\dlt\pipeline\pipeline.py", line 267, in _wrap   
    return f(self, *args, **kwargs)
  File "C:\Users\rahul\OneDrive\Desktop\Work\openapi_hackathon\dlt-init-openapi\env\lib\site-packages\dlt\pipeline\pipeline.py", line 446, in extract 
    raise PipelineStepFailed(
dlt.pipeline.exceptions.PipelineStepFailed: Pipeline execution failed at stage extract when processing package 1716380157.3405726 with exception:     

<class 'dlt.extract.exceptions.ResourceExtractionError'>
In processing pipe bigquery_projects_list: extraction of resource bigquery_projects_list in generator paginate_resource caused an exception: 401 Client Error: Unauthorized for url: https://bigquery.googleapis.com/bigquery/v2/projects?pageToken=0
```

It was also not clear to me how I should define the `secrets.toml` section. I tried `[source.google_bigquery.credentials]`, `[source.rest_api.credentials]`, `[source.credentials]`. This is not a big problem, since I could anyway pass the token to by script using `dlt.secrets.value`, but it would be nice to have a template.


**Note**: The access token is valid. I was able to successfully execute this function by manually passing the access token in a python function 
```
def list_projects(access_token):
    url = "https://bigquery.googleapis.com/bigquery/v2/projects"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        projects = response.json().get('projects', [])
        for project in projects:
            print(f"Project ID: {project['id']}, Project Name: {project['friendlyName']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
```

### Debugging

Not really an actionable, but just an insight based on my usage:

I like the idea behind the open api generator, but I find it less customizable. Usually when I have errors when using a source, I am able to go inside the code, play with it, and find a workaround to get the pipeline to run. But with the rest_api source, there is only the api config, and if you're very familiar with REST API then the source code can be hard to debug and modify.
