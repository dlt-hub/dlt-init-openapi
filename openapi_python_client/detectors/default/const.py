import re

#
# Some settings
#
MAX_RECURSION_DEPTH = 6

# unique key
RE_UNIQUE_KEY = re.compile(r"\b(unique|id|identifier)\b", re.IGNORECASE)

# pagination
RE_OFFSET_PARAM = re.compile(r"(?i)(page|start|offset)", re.IGNORECASE)
RE_LIMIT_PARAM = re.compile(r"(?i)(limit|per_page|page_size|size)", re.IGNORECASE)
RE_TOTAL_PROPERTY = re.compile(r"(?i)(total|count)", re.IGNORECASE)
RE_CURSOR_PARAM = re.compile(r"(?i)(cursor|after|since)", re.IGNORECASE)
RE_NEXT_PROPERTY = re.compile(r"(?i)(next|next_url|more)", re.IGNORECASE)
RE_MATCH_ALL = re.compile(r".*", re.IGNORECASE)
# content path discovery


# parent property discovery
