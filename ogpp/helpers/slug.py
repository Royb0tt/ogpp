from slugify import Slugify, slugify_unicode
import string

VALID_ASCII = string.printable[62:]


class SlugAdapter:
    def __init__(self):
        self.slug = Slugify(to_lower=True)
        self.slug.separator = ''

    def __call__(self, string):
        if any(character not in VALID_ASCII for character in string):
            return slugify_unicode(string).replace('-', '').lower()
        else:
            return self.slug(string)

    def __repr__(self):
        return "SlugAdapter of %r" % self.slug
