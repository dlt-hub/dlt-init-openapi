import re

#
# Some settings
#
MAX_RECURSION_DEPTH = 6
DEFAULT_MAXIMUM_PAGINATOR_OFFSET = 20

# primary key
PRIMAY_KEY_NAMES = ["id", "pk", "unique", "identifier", "primary_key"]
PRIMARY_KEY_SUFFIXES = ["id", "pk"]
PRIMARY_KEY_WORD_SEPARATORS = ["", "-", "_"]

RE_UNIQUE_KEY = re.compile(r"\b(unique|id|identifier)\b", re.IGNORECASE)

# pagination
RE_OFFSET_PARAM = re.compile(r"(?i)(page|start|offset|skip)", re.IGNORECASE)
RE_LIMIT_PARAM = re.compile(r"(?i)(limit|per_page|page_size|size)", re.IGNORECASE)
RE_TOTAL_PROPERTY = re.compile(r"(?i)(total|count)", re.IGNORECASE)
RE_CURSOR_PARAM = re.compile(r"(?i)(cursor|after|since)", re.IGNORECASE)
RE_CURSOR_PROP = re.compile(r"(?i)(cursor|next_cursor)", re.IGNORECASE)
RE_NEXT_PROPERTY = re.compile(r"(?i)(next|next_url|more)", re.IGNORECASE)
RE_MATCH_ALL = re.compile(r".*", re.IGNORECASE)

# content path discovery


# parent property discovery
