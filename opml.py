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


from datetime import datetime
from feedparser import parse
from pony.orm import db_session
from uuid import UUID
from xml.etree import ElementTree

from database import Source as SourceModel, Tag as TagModel, User as UserModel


# TODO: Figure out proper type hint for opml_stream
def import_opml(opml_stream, user_id: UUID) -> None:
    """Imports the tags and feeds from an OPML file.

    :param opml_stream: A file stream containing an OPML file.
    :param user_id: The id of the user importing the file.
    """

    # get the body element from the stream
    tree = ElementTree.parse(opml_stream)
    root_element = tree.getroot()
    body = root_element.find('body')

    with db_session:
        user = UserModel[user_id]

        # recursively iterate through the outlines
        for outline in body:
            process_outline(outline, [], user)


def process_outline(outline: ElementTree.Element, current_tags: list, user: UserModel) -> None:
    """Processes an OPML outline element. Feed elements will be added or updated as necessary, and child tags will be
    recursively processed.

    :param outline: The outline element to process
    :param current_tags: Current tags in this branch of the XML tree
    :param user: The user importing these feeds & tags
    """

    # get the attributes out of the outline
    attrib = outline.attrib

    # is this a feed?
    outline_type = attrib.get('type')
    if outline_type is not None and outline_type == 'rss':
        process_feed_outline(attrib, current_tags, user)
        return

    # if this isn't a feed, it's a tag
    text = attrib['text']
    tag = TagModel.get(label=text, user=user)
    if tag is None:
        tag = TagModel(label=text, user=user)

    # tags can be child elements of other tags (thanks OPML), so if this tag isn't already in the list of tags, add it
    # also need to remember if this branch of the XML tree already has this tag, so we don't remove it prematurely
    if tag in current_tags:
        tag = None
    else:
        current_tags.append(tag)

    # process child outlines
    for child in outline:
        process_outline(child, current_tags, user)

    # remove the tag if this was the outermost instance of the tag
    if tag is not None:
        current_tags.remove(tag)


def process_feed_outline(attrib: dict, current_tags: list, user: UserModel) -> None:
    """Process a feed from an OPML outline element.

    :param attrib: OPML outline attributes for a feed
    :param current_tags: Current tags to associate to feed
    :param user: User importing this feed
    """

    # get address of feed
    uri = attrib['xmlUrl']

    # check if source already exists for feed, update if it does
    source = SourceModel.get(feed_uri=uri)
    if source is not None:
        update_source_tags_and_users(source, current_tags, user)
        return

    # download & parse feed
    feed = parse(uri)

    # get feed info or defaults
    feed_info = feed.get('feed', {})
    label = feed_info.get('title', uri)
    link = feed_info.get('link', uri)

    # build source
    SourceModel(feed_uri=uri, fetched_label=label, last_check=datetime.min, last_fetch=datetime.min, link=link,
                tags=current_tags, users=[user])


def update_source_tags_and_users(source: SourceModel, current_tags: list, user: UserModel) -> None:
    """Make sure that the source's tag and user sets contain the passed tags and user.

    :param source: Source model to be updated
    :param current_tags: Current tags to union into the source's tags
    :param user: User importing this feed, to be added if not already in set of users
    """

    # add tags not currently in the set
    for tag in current_tags:
        if tag in source.tags:
            continue

        source.tags.add(tag)

    # add the current user if not already in the set
    if user in source.users:
        return

    source.users.add(user)
