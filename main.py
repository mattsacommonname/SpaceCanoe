from feedparser import parse
from flask import Flask, render_template


app = Flask(__name__)
feed_uris = [
    'http://thisisindexed.com/feed/',
    'https://www.webtoons.com/en/comedy/behind-the-gifs/rss?title_no=658',
    'https://xkcd.com/atom.xml']


@app.route('/')
def root():
    feeds = []
    for feed_uri in feed_uris:
        feed = parse(feed_uri)
        feeds.append(feed)

    return render_template('root.html', feeds=feeds)
