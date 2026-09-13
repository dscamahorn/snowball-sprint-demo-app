"""A small in-memory store for results handed from one request to the next.

The streaming routes produce a result inside a long-lived response, then the
browser is redirected to a page that displays it. The session cookie is too
small to hold a full set of concepts, so the result waits here under a random
key that is stored in the session instead.

The cache lives in this one Python process. If the app is ever run with more
than one gunicorn worker, a result stored by one worker cannot be found by
another, so the app must run with a single worker.
"""

from collections import OrderedDict

# How many results to keep before the oldest one is dropped. This stops the
# cache from growing forever when a browser disconnects before collecting
# its result.
MAX_ENTRIES = 100


class ResultCache:
    """Stores results by key and forgets the oldest entry when it is full."""

    def __init__(self, max_entries=MAX_ENTRIES):
        """Start empty. max_entries caps how many results are kept."""
        # OrderedDict remembers insertion order, so the first key is the oldest.
        self.entries = OrderedDict()
        self.max_entries = max_entries

    def store(self, key, value):
        """Save a result under the given key, evicting the oldest if over capacity."""
        self.entries[key] = value
        if len(self.entries) > self.max_entries:
            # last=False removes the oldest entry rather than the newest.
            self.entries.popitem(last=False)

    def contains(self, key) -> bool:
        """Return True if a result is waiting under this key."""
        return key in self.entries

    def take(self, key):
        """Remove the result stored under the key and return it. Each result is read once."""
        return self.entries.pop(key)


# The two shared caches used by the routes.
research_result_cache = ResultCache()
concept_result_cache = ResultCache()
