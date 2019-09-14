# Do not leave this as True in production environments, it will allow the execution of arbitrary code.

DEBUG: bool = True

# Change this. Here is an example way to generate one:
#
# python -c 'import os; print(os.urandom(16))'

SECRET_KEY: bytes = b'changeme'

# Pony ORM database bindings

PONY_BINDINGS: dict = {'provider': 'sqlite', 'filename': 'data/feeds.sqlite', 'create_db': True}

# Generate Pony ORM bindings

PONY_MAPPINGS: dict = {'create_tables': True}
