from datetime import datetime
from feedparser import parse
from pony.orm import db_session
from xml.etree import ElementTree

from database import Source as SourceModel, Tag as TagModel


def process_outline(outline: ElementTree.Element, current_tags: list):
    attrib = outline.attrib

    outline_type = attrib.get('type')
    if outline_type is not None and outline_type == 'rss':
        uri = attrib['xmlUrl']

        source = SourceModel.get(feed_uri=uri)
        if source is not None:
            for tag in current_tags:
                if tag in source.tags:
                    continue

                source.tags.add(tag)
            return

        feed = parse(uri)
        print(f'parsing {uri}')
        SourceModel(feed_uri=uri, label=feed['feed']['title'], last_check=datetime.min, last_fetch=datetime.min,
                    link=feed['feed']['link'], tags=current_tags)

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


def import_opml(opml_stream):
    tree = ElementTree.parse(opml_stream)

    root_element = tree.getroot()
    body = root_element.find('body')

    with db_session:
        for outline in body:
            process_outline(outline, [])