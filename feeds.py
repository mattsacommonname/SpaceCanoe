from calendar import timegm
from datetime import datetime
from feedparser import parse
from pony.orm import db_session, select

from database import Entry as EntryModel, Source as SourceModel


datetime_min_tuple = datetime.min.timetuple()


def process_entries(entries, source: SourceModel):
    for entry in entries:
        # build UTC time
        updated = entry.get('updated_parsed', datetime_min_tuple)
        timestamp = timegm(updated)
        updated = datetime.utcfromtimestamp(timestamp)

        link = entry.get('link', None)
        if not link:  # no point to an entry without a link
            continue

        title = entry.get('title', link) or link
        summary = entry.get('summary', '')

        check = EntryModel.get(link=link, source=source, title=title, updated=updated)
        if check is not None:
            continue

        EntryModel(link=link, source=source, summary=summary, title=title, updated=updated)


def check_for_updates():
    with db_session:
        sources = select(s for s in SourceModel)
        for source in sources:
            now = datetime.now()

            feed = parse(source.feed_uri)
            source.last_check = now

            if feed['bozo']:
                continue

            source.last_fetch = now

            process_entries(feed['entries'], source)
