# Space Canoe

Self-hosted feed reader.

## Installation

1. Create a Python virtual environment. Or don't, I'm not your dad.
2. Run  the following commands:
   ```
   pip install -r requirements.txt
   export FLASK_APP=main
   export FLASK_DEBUG=1
   ```
3. Reset the database (see Use section).

## Use

### Reset the database

`flask reset URIFILEPATH`

`URIFILEPATH` should be the path of a text file that contains urls for a feed, one per line.

Running this will wipe-out all data.

### Fetch and update the entries in the database

`flask update`

Fetches and parses feeds, adding new entries to the database.

### Run the server

`flask run` 

Runs the flask application.
