from flask_login import login_required
from flask_restful import fields, marshal, Resource
from pony.orm import db_session, desc, select

from database import Entry as EntryModel


source_in_entry_fields = {
    'link': fields.String,
    'label': fields.String
}


entry_fields = {
    'link': fields.String,
    'source': fields.Nested(source_in_entry_fields),
    'summary': fields.String,
    'title': fields.String,
    'updated': fields.DateTime
}


class Entries(Resource):
    decorators = [login_required]

    @staticmethod
    def get():
        with db_session:
            result = select(e for e in EntryModel).order_by(desc(EntryModel.updated))
            entries = list(result)
            output = marshal(entries, entry_fields)
            return output
