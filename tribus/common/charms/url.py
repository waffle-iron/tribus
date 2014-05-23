import copy
import re

from tribus.common.charms.errors import CharmURLError


_USER_RE = re.compile("^[a-z0-9][a-zA-Z0-9+.-]+$")
_SERIES_RE = re.compile("^[a-z]+([a-z-]+[a-z])?$")
_NAME_RE = re.compile("^[a-z][a-z0-9]*(-[a-z0-9]*[a-z][a-z0-9]*)*$")


class CharmURL(object):
    """Holds enough information to specify a charm.

    :attr path: Where to look for the charm.
    :type path: str

    :attr str name: The charm's name.
    """

    def __init__(self, path, name):
        self.path = path
        self.name = name

    def __str__(self):
        return "%s/%s" % (self.path, self.name)

# 
#     def with_revision(self, revision):
#         other = copy.deepcopy(self)
#         other.revision = revision
#         return other
# 
#     def assert_revision(self):
#         if self.revision is None:
#             raise CharmURLError(str(self), "expected a revision")

#     @classmethod
#     def parse(cls, string):
#         """Turn an unambiguous string representation into a CharmURL."""
# 
#         def fail(message):
#             raise CharmURLError(string, message)
# 
#         if not isinstance(string, basestring):
#             fail("not a string type")
#         if ":" not in string:
#             fail("no schema specified")
#         schema, rest = string.split(":", 1)
#         if schema not in ("cs", "local"):
#             fail("invalid schema")
# 
#         parts = rest.split("/")
#         if len(parts) not in (2, 3):
#             fail("invalid form")
# 
#         user = None
#         if parts[0].startswith("~"):
#             if schema == "local":
#                 fail("users not allowed in local URLs")
#             user = parts[0][1:]
#             if not _USER_RE.match(user):
#                 fail("invalid user")
#             parts = parts[1:]
# 
#         if len(parts) != 2:
#             fail("no series specified")
# 
#         revision = None
#         series, name = parts
#         if not _SERIES_RE.match(series):
#             fail("invalid series")
#         if "-" in name:
#             maybe_name, maybe_revision = name.rsplit("-", 1)
#             if maybe_revision.isdigit():
#                 name, revision = maybe_name, int(maybe_revision)
#         if not _NAME_RE.match(name):
#             fail("invalid name")
# 
#         return cls(CharmCollection(schema, user, series), name, revision)
# 
#     @classmethod
#     def infer(cls, vague_name, default_series):
#         """Turn a potentially fuzzy alias into a CharmURL."""
#         try:
#             # it might already be a valid URL string
#             return cls.parse(vague_name)
#         except CharmURLError:
#             # ok, it's not, we have to do some work
#             pass
# 
#         if vague_name.startswith("~"):
#             raise CharmURLError(
#                 vague_name, "a URL with a user must specify a schema")
# 
#         if ":" in vague_name:
#             schema, rest = vague_name.split(":", 1)
#         else:
#             schema, rest = "cs", vague_name
# 
#         url_string = "%s:%s" % (schema, rest)
#         parts = rest.split("/")
#         if len(parts) == 1:
#             url_string = "%s:%s/%s" % (schema, default_series, rest)
#         elif len(parts) == 2:
#             if parts[0].startswith("~"):
#                 url_string = "%s:%s/%s/%s" % (
#                     schema, parts[0], default_series, parts[1])
# 
#         try:
#             return cls.parse(url_string)
#         except CharmURLError as err:
#             err.message += " (URL inferred from '%s')" % vague_name
#             raise
