from feedparser import parse
from flask import Flask, render_template
from pony.orm import Database, db_session, Required, select, Set, set_sql_debug


app = Flask(__name__)
db = Database()


class Source(db.Entity):
    label = Required(str)
    uri = Required(str)


db.bind(provider='sqlite', filename='feeds.sqlite', create_db=True)
set_sql_debug(True)
db.generate_mapping(create_tables=True)


@app.cli.command()
def initdb():
    with db_session:
        Source(label='Behind the GIFs', uri='https://www.webtoons.com/en/comedy/behind-the-gifs/rss?title_no=658')
        Source(label='Indexed', uri='http://thisisindexed.com/feed/')
        Source(label='XKCD', uri='https://xkcd.com/atom.xml')


@app.route('/')
def root():
    feeds = []
    with db_session:
        sources = select(s for s in Source)
        for source in sources:
            feed = parse(source.uri)
            feeds.append(feed)

    return render_template('root.html', feeds=feeds)
