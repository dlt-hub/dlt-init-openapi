# marvel pipeline

Created with [dlt-openapi](https://github.com/dlt-hub/dlt-openapi) v. 0.0.2

* https://dlthub.com
* https://github.com/dlt-hub/dlt
* https://github.com/dlt-hub/dlt-openapi


## Available resources
* get_creator_collection  
  _GET /v1/public/characters_  
Fetches lists of comic characters with optional filters. See notes on individual parameters below.* get_character_individual  
  _GET /v1/public/characters/{characterId}_  
This method fetches a single character resource.  It is the canonical URI for any character resource provided by the API.* get_creator_collection  
  _GET /v1/public/stories/{storyId}/characters_  
Fetches lists of comic characters appearing in a single story, with optional filters. See notes on individual parameters below.* get_comics_collection  
  _GET /v1/public/comics_  
Fetches lists of comics with optional filters. See notes on individual parameters below.* get_comic_individual  
  _GET /v1/public/comics/{comicId}_  
This method fetches a single comic resource.  It is the canonical URI for any comic resource provided by the API.* get_comics_collection  
  _GET /v1/public/creators/{creatorId}/comics_  
Fetches lists of comics in which the work of a specific creator appears, with optional filters. See notes on individual parameters below.* get_comics_collection  
  _GET /v1/public/events/{eventId}/comics_  
Fetches lists of comics which take place during a specific event, with optional filters. See notes on individual parameters below.* get_comics_collection  
  _GET /v1/public/series/{seriesId}/comics_  
Fetches lists of comics which are published as part of a specific series, with optional filters. See notes on individual parameters below.* get_comics_collection  
  _GET /v1/public/stories/{storyId}/comics_  
Fetches lists of comics in which a specific story appears, with optional filters. See notes on individual parameters below.* get_creator_collection  
  _GET /v1/public/comics/{comicId}/creators_  
Fetches lists of comic creators whose work appears in a specific comic, with optional filters. See notes on individual parameters below.* get_creator_collection  
  _GET /v1/public/creators_  
Fetches lists of comic creators with optional filters. See notes on individual parameters below.* get_creator_collection  
  _GET /v1/public/events/{eventId}/creators_  
Fetches lists of comic creators whose work appears in a specific event, with optional filters. See notes on individual parameters below.* get_creator_collection  
  _GET /v1/public/series/{seriesId}/creators_  
Fetches lists of comic creators whose work appears in a specific series, with optional filters. See notes on individual parameters below.* get_creator_collection  
  _GET /v1/public/stories/{storyId}/creators_  
Fetches lists of comic creators whose work appears in a specific story, with optional filters. See notes on individual parameters below.