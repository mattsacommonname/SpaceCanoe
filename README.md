# Space Canoe

Self-hosted feed reader.

## Installation

1. Create a Python virtual environment. Or don't, I'm not your dad.
2. Run  the following commands:
   ```
   pip install -r requirements.txt
   export FLASK_APP=main
   ```
3. Copy `defaultconfig.py` to `data/config.py`. Edit the values as necessary. At least change the `SECRET_KEY`.
4. See the *Use* section.

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

## License

Copyright 2019 Matthew Bishop

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
