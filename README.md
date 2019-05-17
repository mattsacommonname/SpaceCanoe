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
3. See the *Use* section.

## Use

### Add a user

`flask au USERNAME PASSWORD`

### Run the server

`flask run` 

Runs the flask application.

### Import an OPML file

Browse to the page, click on **Choose File**, then choose an [OPML](http://dev.opml.org/spec2.html#subscriptionLists)
file. Then click **Upload**.

### Fetch and update the entries in the database

`flask up`

Fetches and parses feeds, adding new entries to the database.
