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
from xml.etree import ElementTree

from database import Source as SourceModel, Tag as TagModel


broken_feed = {
    'title': 'unknown',
    'link': 'null'
}


def import_opml(opml_stream):
    tree = ElementTree.parse(opml_stream)

    root_element = tree.getroot()
    body = root_element.find('body')

    with db_session:
        for outline in body:
            process_outline(outline, [])


def process_outline(outline: ElementTree.Element, current_tags: list):
    attrib = outline.attrib

    outline_type = attrib.get('type')
    if outline_type is not None and outline_type == 'rss':
        process_rss_outline(attrib, current_tags)
        return

    text = attrib['text']
    tag = TagModel.get(label=text)
    if tag is None:
        tag = TagModel(label=text)

    if tag in current_tags:
        tag = None
    else:
        current_tags.append(tag)

    for child in outline:
        process_outline(child, current_tags)

    if tag is not None:
        current_tags.remove(tag)


def process_rss_outline(attrib, current_tags: list):
    uri = attrib['xmlUrl']

    source = SourceModel.get(feed_uri=uri)
    if source is not None:
        update_source(source, current_tags)
        return

    feed = parse(uri)
    feed_info = feed.get('feed', broken_feed)
    label = feed_info.get('title', broken_feed['title']) or uri
    link = feed_info.get('link', broken_feed['link']) or uri

    SourceModel(feed_uri=uri, label=label, last_check=datetime.min, last_fetch=datetime.min, link=link,
                tags=current_tags)


def update_source(source: SourceModel, current_tags: list):
    for tag in current_tags:
        if tag in current_tags:
            continue

        source.tags.add(tag)
