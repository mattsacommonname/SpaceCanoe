from calendar import timegm
from click import Argument, Command
from datetime import datetime
from feedparser import parse
from pony.orm import db_session, delete, select

from database import Entry as EntryModel, Source as SourceModel, User as UserModel


def adduser(name, password):
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
AddUserCommand = Command('adduser', callback=adduser, params=params)


def reset(uri_file_path):
    earliest = datetime.min
    with db_session:
        delete(s for s in SourceModel)
        delete(e for e in EntryModel)

        with open(uri_file_path) as f:
            for line in f:
                uri = line.strip()
                if not uri:
                    continue

                feed = parse(uri)
                SourceModel(feed_uri=uri, label=feed['feed']['title'], last_check=earliest, last_fetch=earliest,
                            link=feed['feed']['link'])


arg = Argument(('uri_file_path',))
params = [arg]
ResetCommand = Command('reset', callback=reset, params=params)


def update():
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


UpdateCommand = Command('update', callback=update)
