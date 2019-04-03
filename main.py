from feedparser import FeedParserDict, parse


feed_uris = [
    'http://thisisindexed.com/feed/',
    'https://www.webtoons.com/en/comedy/behind-the-gifs/rss?title_no=658',
    'https://xkcd.com/atom.xml']


def parse_entry(entry: FeedParserDict):
    print(entry['title'])


def parse_feed(uri: str):
    try:
        feed = parse(uri)

    except Exception as ex:
        print(ex)
        return

    if feed is None or feed.bozo:
        print(f'\n"{uri}" did not resolve\n')
        return

    print(f"\n{feed['feed']['title']}\n")

    for entry in feed['entries']:
        parse_entry(entry)


for feed_uri in feed_uris:
    parse_feed(feed_uri)
