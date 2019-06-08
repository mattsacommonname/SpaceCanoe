# Copyright 2019 Matthew Bishop
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from calendar import timegm
from datetime import datetime
from feedparser import parse
from pony.orm import db_session, select

from database import Entry as EntryModel, Source as SourceModel


def utc_timestamp_from_tuple(parsed_tuple: tuple):
    """Generates a date & time in UTC given a date & time tuple.

    :param parsed_tuple: A date-time tuple in the format (, )
    :return: A datetime object in UTC.
    """

    if not parsed_tuple:
        return datetime.min

    timestamp = timegm(parsed_tuple)
    utc_datetime = datetime.utcfromtimestamp(timestamp)
    return utc_datetime


def process_entries(entries, source: SourceModel):
    """Iterate through entries (presumably from a feed), add the new ones to the database.

    :param entries: The entries from the feed.
    :param source: The source that the entries should be associated with.
    """

    for entry in entries:
        # build UTC time
        updated_parsed = entry.get('updated_parsed', None)
        updated = utc_timestamp_from_tuple(updated_parsed)

        link = entry.get('link', None)
        if not link:  # no point to an entry without a link
            continue

        title = entry.get('title', link) or link
        summary = entry.get('summary', '')

        # check if this entry already exists
        check = EntryModel.get(link=link, source=source, title=title, updated=updated)
        if check is not None:
            continue

        # unique entry, add it
        EntryModel(link=link, source=source, summary=summary, title=title, updated=updated)


def update_feeds():
    """Checks all sources for feed updates."""

    with db_session:
        sources = select(s for s in SourceModel)
        for source in sources:
            now = datetime.now()

            # fetch & parse feed
            feed = parse(source.feed_uri)
            source.last_check = now

            # check if download was successful
            if feed['bozo']:
                continue

            # update with new data
            label = source.fetched_label
            # source.fetched_label = feed[''] or label
            source.fetched_label = feed.get('feed', {}).get('title', label)
            source.last_fetch = now

            # check for and process new entries
            process_entries(feed['entries'], source)
