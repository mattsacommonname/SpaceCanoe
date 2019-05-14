from calendar import timegm
from click import Argument, Command
from datetime import datetime
from feedparser import parse
from pony.orm import db_session, select
from xml.etree import ElementTree

from database import Entry as EntryModel, Source as SourceModel, Tag as TagModel, User as UserModel


def add_user(name, password):
    with db_session:
        model = UserModel.get(name=name)
        if model:
            print(f'User "{name}" already exists.')
            return

        UserModel.build(name, password)


arg = Argument(('name',))
params = [arg]
arg = Argument(('password',))
params.append(arg)
AddUserCommand = Command('au', callback=add_user, params=params)


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


def import_opml(opml_path):
    with open(opml_path) as f:
        tree = ElementTree.parse(f)

        root = tree.getroot()
        body = root.find('body')

        with db_session:
            for outline in body:
                process_outline(outline, [])


arg = Argument(('opml_path',))
params = [arg]
ResetCommand = Command('io', callback=import_opml, params=params)


def check_for_updates():
    sources_processed = 0
    entries_processed = 0
    entries_added = 0

    with db_session:
        sources = select(s for s in SourceModel)
        for source in sources:
            feed = parse(source.feed_uri)
            if feed['bozo']:
                continue

            sources_processed += 1
            now = datetime.now()
            source.last_check = now
            source.last_fetch = now

            for entry in feed['entries']:
                # build UTC time
                timestamp = timegm(entry['updated_parsed'])
                updated = datetime.utcfromtimestamp(timestamp)

                link = entry['link']
                title = entry['title']

                entries_processed += 1

                check = EntryModel.get(link=link, source=source, title=title, updated=updated)
                if check is not None:
                    continue

                entries_added += 1

                EntryModel(link=link, source=source, summary=entry['summary'], title=title, updated=updated)

    print(f'sources processed\t{sources_processed}\nentries processed\t{entries_processed}',
          f'entries added\t{entries_added}', sep='\n')


UpdateCommand = Command('up', callback=check_for_updates)
