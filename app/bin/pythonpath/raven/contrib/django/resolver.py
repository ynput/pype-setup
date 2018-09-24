from __future__ import absolute_import

import re

try:
    from django.urls import get_resolver
except ImportError:
    from django.core.urlresolvers import get_resolver


class RouteResolver(object):
    _optional_group_matcher = re.compile(r'\(\?\:([^\)]+)\)')
    _named_group_matcher = re.compile(r'\(\?P<(\w+)>[^\)]+\)')
    _non_named_group_matcher = re.compile(r'\([^\)]+\)')
    # [foo|bar|baz]
    _either_option_matcher = re.compile(r'\[([^\]]+)\|([^\]]+)\]')
    _camel_re = re.compile(r'([A-Z]+)([a-z])')

    _cache = {}

    def _simplify(self, pattern):
        """
        Clean up urlpattern regexes into something readable by humans:

        From:
        > "^(?P<sport_slug>\w+)/athletes/(?P<athlete_slug>\w+)/$"

        To:
        > "{sport_slug}/athletes/{athlete_slug}/"
        """
        # remove optional params
        # TODO(dcramer): it'd be nice to change these into [%s] but it currently
        # conflicts with the other rules because we're doing regexp matches
        # rather than parsing tokens
        result = self._optional_group_matcher.sub(lambda m: '%s' % m.group(1), pattern)

        # handle named groups first
        result = self._named_group_matcher.sub(lambda m: '{%s}' % m.group(1), result)

        # handle non-named groups
        result = self._non_named_group_matcher.sub('{var}', result)

        # handle optional params
        result = self._either_option_matcher.sub(lambda m: m.group(1), result)

        # clean up any outstanding regex-y characters.
        result = result.replace('^', '').replace('$', '') \
            .replace('?', '').replace('//', '/').replace('\\', '')

        return result

    def _resolve(self, resolver, path, parents=None):
        match = resolver.regex.search(path)
        if not match:
            return

        if parents is None:
            parents = [resolver]
        elif resolver not in parents:
            parents = parents + [resolver]

        new_path = path[match.end():]
        for pattern in resolver.url_patterns:
            # this is an include()
            if not pattern.callback:
                match = self._resolve(pattern, new_path, parents)
                if match:
                    return match
                continue

            elif not pattern.regex.search(new_path):
                continue

            try:
                return self._cache[pattern]
            except KeyError:
                pass

            prefix = ''.join(self._simplify(p.regex.pattern) for p in parents)
            result = prefix + self._simplify(pattern.regex.pattern)
            if not result.startswith('/'):
                result = '/' + result
            self._cache[pattern] = result
            return result

    def resolve(self, path, urlconf=None):
        resolver = get_resolver(urlconf)
        match = self._resolve(resolver, path)
        return match or path
