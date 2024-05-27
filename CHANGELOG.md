[Go to GitHub Releases](https://github.com/dlt-hub/dlt-init-openapi/releases)

0.1.0a3 - Getting ready for the first release
* Remove left over print statement
* Small udpates to readme

0.1.0a2 - Getting ready for the first release
* Updated Readme, reordered content blocks and made example nicer
* Better rendering of required and non-required query args
* Do not ask wether output directory should be written when in non-interactive mode

0.1.0a1 - Getting ready for the first release
* Remove init command from CLI. The same functionality is now the default command, see updated README file.
* Add better error messages for broken and incompatible specs
* Add a basic contributing page
* Improve endpoint selector message and select all endpoints if nothing is selected by the user
* Add endpoint descriptions as comments to the rendered source
* Fixes in paginator detection
* Add location of original spec to the generated README
* Add flag to allow OpenAPI 2.0 specs. Update readme with all current flags

0.0.5a3 - Internal Preview 3
* Render gitignore file and add source section to secrets.toml even if there are no secrets detected
* Updated readme with feedback from users and added pip instructions
* Make "username" a secret on basic auth
* Prevent openapi 2.0 specs with helpful output on how to migrate
* Fix e2e tests

0.0.5a2 - Internal Preview 2
* Better fallbacks for paginator and json_path if detection failed
* Add telemetry on init command
* Sanitze and snake case folders and files output

0.0.5a1 - Internal Preview 1
* pypi package and rename, pyproject fixes 0.0.5a1 pypi release

0.0.4 - Dev Alpha Release
* Project rename to dlt-init-openapi
* Pypi alpha release

0.0.3 - Dev Alpha Release
* add param defaults & render not required query params
* add support for paths with vars and file-ending
* correct behavior for paginators with unknown total_path
* auth improvements: select correct global auth, add secrets to secrets.toml, add note in readme if secret present

0.0.2 - Dev Alpha Release
* Add warnings to logger for certain scenarios
* Add global paginator support
* Internally refactor auth and add warning for unsupported auth types

0.0.1 - Initial Release
* Initial Release