# Do not leave this as True in production environments, it will allow the execution of arbitrary code.

DEBUG = True

# Change this. Here is an example way to generate one:
#
# python -c 'import os; print(os.urandom(16))'

SECRET_KEY = b'changeme'

# Pony ORM database bindings

PONY_BINDINGS = {'provider': 'sqlite', 'filename': 'data/feeds.sqlite', 'create_db': True}

# Generate Pony ORM bindings

PONY_MAPPINGS = {'create_tables': True}
