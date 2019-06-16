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
from feedparser import parse, FeedParserDict
from pony.orm import db_session, select
from time import struct_time
from typing import List

from database import Entry as EntryModel, Source as SourceModel, SourceUserData as SourceUserDataModel,\
    Tag as TagModel, User as UserModel


def fetch_and_store_feed(url: str, tags: List[TagModel], user: UserModel) -> None:
    """Fetches a feed from the given URL, parses it, adds a source if necessary, updates one if it already exists.

    :param url: The URL of the feed.
    :param tags: Tags to add to the source.
    :param user: User adding/updating this feed.
    """

    source = get_or_build_source(url)

    user_data = SourceUserDataModel.get(user=user, source=source)
    if user_data is not None:
        update_tags(user_data, tags)
        return

    SourceUserDataModel(source=source, tags=tags, user=user)


def get_or_build_source(url: str) -> SourceModel:
    """Retrieves an already stored source, or build one from the feed data and stores it.

    :param url: URL of the feed.
    :return: The retrieved/built source.
    """

    source = SourceModel.get(feed_uri=url)
    if source is not None:
        return source

    feed = parse(url)

    # get feed info or defaults
    feed_info = feed.get('feed', {})
    label = feed_info.get('title', url)
    link = feed_info.get('link', url)

    source = SourceModel(feed_uri=url, fetched_label=label, last_check=datetime.min, last_fetch=datetime.min, link=link)
    return source


def utc_timestamp_from_struct_time(parsed_time: struct_time) -> datetime:
    """Generates a date & time in UTC given a struct_time.

    :param parsed_time: A date-time tuple in the format (year, month, day, hour, minute, second).
    :return: A datetime object in UTC.
    """

    # give minimum valid time
    if not parsed_time:
        return datetime.min

    timestamp = timegm(parsed_time)
    utc_datetime = datetime.utcfromtimestamp(timestamp)
    return utc_datetime


def process_entries(entries: List[FeedParserDict], source: SourceModel) -> None:
    """Iterate through entries (presumably from a feed), add the new ones to the database.

    :param entries: The entries from the feed.
    :param source: The source that the entries should be associated with.
    """

    for entry in entries:
        # build UTC time
        updated_parsed = entry.get('updated_parsed', None)
        updated = utc_timestamp_from_struct_time(updated_parsed)

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


def update_feeds() -> None:
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

            # update with new data, if we have any; use the old data otherwise
            label = source.fetched_label
            source.fetched_label = feed.get('feed', {}).get('title', label)
            source.last_fetch = now

            # check for and process new entries
            process_entries(feed['entries'], source)


def update_tags(user_data: SourceUserDataModel, tags: List[TagModel]) -> None:
    """Add any tags missing from the source user data's tag.

    :param user_data: The source user data to update.
    :param tags: Collection of tags to add.
    """

    # add tags not currently in the set
    for tag in tags:
        if tag in user_data.tags:
            continue

        user_data.tags.add(tag)
