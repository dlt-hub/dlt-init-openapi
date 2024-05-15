# pollenrapporten pipeline

Created with [dlt-openapi](https://github.com/dlt-hub/dlt-openapi) v. 0.0.1

* https://dlthub.com
* https://github.com/dlt-hub/dlt
* https://github.com/dlt-hub/dlt-openapi

## Available resources
* pollen_types  
  _GET /v1/pollen-types_  
List all available pollen types.

A pollen type entry contains all the information needed to present a specific pollen type. A pollen type can be references using a `pollen_id`.

The ID of a pollen type, as `pollen_id`, is used to filter other endpoints such as `forecast`.* pollen_level_definitions  
  _GET /v1/pollen-level-definitions_  
List all available pollen level definitions.

A pollen level definition can be used to describe a `PollenLevelValue` found in a `PollenLevel` from `forecast`.* regions  
  _GET /v1/regions_  
List all regions.

Regions are used to identify a limited area to which a forecast is related. Regions can be large or small depending on the use case.

The `id` of region can be used as `region_id` in other endpoints such as `forecasts`* forecasts  
  _GET /v1/forecasts_  
List forecasts filtering on a selection of parameters

To fetch only current data for each region use the parameter `current=true`* pollen_count  
  _GET /v1/pollen-count_  
List a filtered set of daily pollen counts