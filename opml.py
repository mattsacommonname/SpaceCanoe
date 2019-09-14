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


from pony.orm import db_session
from typing import Optional
from uuid import UUID
from xml.etree.ElementTree import Element, ElementTree, parse

from database import Tag as TagModel, User as UserModel
from feeds import fetch_and_store_feed


# TODO: Figure out proper type hint for opml_stream
def import_opml(opml_stream, user_id: UUID) -> None:
    """Imports the tags and feeds from an OPML file.

    :param opml_stream: A file stream containing an OPML file.
    :param user_id: The id of the user importing the file.
    """

    # get the body element from the stream
    tree: ElementTree = parse(opml_stream)
    root_element: Element = tree.getroot()
    body: Element = root_element.find('body')

    with db_session:
        user: UserModel = UserModel[user_id]

        # recursively iterate through the outlines
        for outline in body:
            process_outline(outline, [], user)


def process_outline(outline: Element, current_tags: list, user: UserModel) -> None:
    """Processes an OPML outline element. Feed elements will be added or updated as necessary, and child tags will be
    recursively processed.

    :param outline: The outline element to process
    :param current_tags: Current tags in this branch of the XML tree
    :param user: The user importing these feeds & tags
    """

    # get the attributes out of the outline
    attrib: dict = outline.attrib

    # is this a feed?
    outline_type: str = attrib.get('type')
    if outline_type is not None and outline_type == 'rss':
        url: str = attrib.get('xmlUrl')
        fetch_and_store_feed(url, current_tags, user)
        return

    # if this isn't a feed, it's a tag
    text: str = attrib['text']
    tag: Optional[TagModel] = TagModel.get(label=text, user=user)
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
