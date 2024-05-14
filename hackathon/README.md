# OpenAPI Generator Hackathon!

Welcome to our OpenAPI Generator Hackathon. We want to test how well our generator works, this includes testing the quality of the main repo README.md file as well as the output and usage of the cli. To complete the hackathon, simply follow these steps:

1. Select any api you wish to get data from and which has an OpenAPI spec. We have collected a bunch of specs in [this repo](https://github.com/dlt-hub/openapi-specs/tree/main/open_api_specs) which you can use, but any other will do. Do not forget you might need credentials to get data, so select something you have credentials to.

2. Follow the steps outlined in the main readme of this repo https://github.com/dlt-hub/dlt-openapi to generate and run a pipeline. Please **generate an run your pipeline from this hackathon folder** in this repo. Read additional docs as linked in the main repo if something is unclear.

3. Make notes! A couple of questions for inspiration are listed below.

4. Create a PR on this repo which includes your generated files and the original spec (or a link to the original spec). Add all your notes in the PR comments.

5. That's it, thanks for helping out :)

## Questions

You can give us any notes you like. If you do not know what to write in your notes, here are some questions you can think about while creating the notes.

1. Is it at all clear why we have created this and why it is useful and what it is about?

2. Is it clear how the generator works? Did you manage to generate anything in the first 10 Minutes after selecting a spec? What is missing from the setup instructions or the output of the generator?

3. Is the resulting dlt rest_api source legible? Should it be structured differently or annotated with comments better?

4. Could you run the pipeline after generation? Did it produce some data?

5. If something failed, was the reason for the failure clear? What error message would've been better?

6. Was anything incorrectly converted from the spec to the rest_api definition although it is clear how it should've been generated? If so, which section and what should've been produced?

7. Are there any settings or options or commands you are missing from the tool?

## Notes

* Oauth currently is not supported.

* If you need better logging output while **running** the pipeline (after generating it), you can increase the dlt loglevel as described in the [docs](https://dlthub.com/docs/running-in-production/running#set-the-log-level-and-format).

* Problems that happen during running of the pipeline may actually be stuff to fix in the rest_api or rest_client, but you can add all of this feedback to this hackathon and we will figure out what goes where.