from calendar import timegm
from click import argument
from datetime import datetime
from feedparser import parse
from flask import Flask, render_template
from flask_restful import Api, fields, marshal, Resource
from pony.orm import composite_key, Database, db_session, delete, desc, Optional, Required, select, Set, set_sql_debug


app = Flask(__name__)
api = Api(app)
db = Database()


class Source(db.Entity):
    feed_uri = Required(str, unique=True)
    entries = Set('Entry')
    label = Required(str)
    last_check = Required(datetime)
    last_fetch = Required(datetime)
    link = Required(str)


class Entry(db.Entity):
    link = Required(str)
    source = Required(Source)
    summary = Optional(str)
    title = Required(str)
    updated = Required(datetime)
    composite_key(source, link, title, updated)


source_in_entry_fields = {
    'link': fields.String,
    'label': fields.String
}


entry_fields = {
    'link': fields.String,
    'source': fields.Nested(source_in_entry_fields),
    'summary': fields.String,
    'title': fields.String,
    'updated': fields.DateTime
}


class Entries(Resource):
    def get(self):
        with db_session:
            result = select(e for e in Entry).order_by(desc(Entry.updated))
            entries = list(result)
            output = marshal(entries, entry_fields)
            return output


api.add_resource(Entries, '/entries')


db.bind(provider='sqlite', filename='feeds.sqlite', create_db=True)
set_sql_debug(True)
db.generate_mapping(create_tables=True)


@app.cli.command()
@argument('uri_file_path')
def reset(uri_file_path):
    earliest = datetime.min
    with db_session:
        delete(s for s in Source)
        delete(e for e in Entry)

        with open(uri_file_path) as f:
            for line in f:
                uri = line.strip()
                if not uri:
                    continue

                feed = parse(uri)
                Source(feed_uri=uri, label=feed['feed']['title'], last_check=earliest, last_fetch=earliest,
                       link=feed['feed']['link'])


@app.route('/')
def root():
    with db_session:
        entries = select(e for e in Entry).order_by(desc(Entry.updated))

        output = render_template('root.html', entries=entries)

    return output


@app.cli.command()
def update():
    with db_session:
        sources = select(s for s in Source)
        for source in sources:
            feed = parse(source.feed_uri)
            if feed['bozo']:
                continue

            for entry in feed['entries']:
                # build UTC time
                timestamp = timegm(entry['updated_parsed'])
                updated = datetime.utcfromtimestamp(timestamp)

                link = entry['link']
                title = entry['title']

                check = Entry.get(link=link, source=source, title=title, updated=updated)
                if check is not None:
                    continue

                Entry(link=link, source=source, summary=entry['summary'], title=title, updated=updated)
