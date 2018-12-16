"""This is some module documentation"""

from django.http import HttpResponse
from hamcrest.core.helpers.wrap_matcher import wrap_matcher
from hamcrest.core.string_description import StringDescription
from pyhamcrest_toolbox.multicomponent import (
    MatcherPlugin,
    MulticomponentMatcher
)
from pyhamcrest_toolbox.util import (
    get_description
)
from pyhamcrest_toolbox.wrapper_base import MatcherPluginWrapper
from pyhamcrest_toolbox.wrappers import InstanceOfPlugin, IsAnythingPlugin

from django_pyhamcrest.matchers.cookie import CookieMatcher


class HeadersMatcher(MatcherPlugin):
    def __init__(self, headers_dict):
        super().__init__()
        self.headers_ = {
            key: wrap_matcher(value) for key, value in headers_dict.items()
        }
        self.errors = []


    def component_matches(self, item):
        matches = True
        for header, matcher in self.headers_.items():
            if not item.has_header(header):
                matches = False
                self.errors.append("does not contain header <{}>".format(header))
            elif not matcher._matches(item[header]):
                matches = False
                descr = StringDescription()
                matcher.describe_mismatch(item[header], descr)
                self.errors.append("the value for header <{}> was <{}>".format(
                    header, str(descr)))
        return matches


    def describe_to(self, description):
        header_descr = [
            "{}: {}".format(key, get_description(val))
            for key, val in self.headers_.items()]
        description.append_text(
            "with headers: {{{}}}".format(", ".join(header_descr)))


    def describe_component_mismatch(self, item, mismatch_description):
        mismatch_description.append_text(", ".join(self.errors))


class StatusMatcher(MatcherPluginWrapper):
    description_prefix = "with status_code "
    mismatch_description_prefix = "the status_code "


    def convert_item(self, item):
        return item.status_code


class CookieComponentMatcher(MatcherPluginWrapper):
    description_prefix = "with cookies "
    mismatch_description_prefix = "the cookies"
    matcher_class = CookieMatcher

    def convert_item(self, item):
        return item.cookies


class ContentMatcher(MatcherPluginWrapper):
    description_prefix = "with content "
    mismatch_description_prefix = "the content "

    def convert_item(self, item):
        return item.content


class ResponseMatcher(MulticomponentMatcher):
    """HEllo. let's see if it appears in the doc"""
    def __init__(self):
        super().__init__()
        self.register(InstanceOfPlugin(HttpResponse))


    def with_status(self, status_code):
        if status_code is None:
            self.register(IsAnythingPlugin("with any status_code"))
        else:
            self.register(StatusMatcher(status_code))
        return self


    def with_headers(self, headers_dict):
        """Adds the check for headers.

        :param headers_dict: dict {key:  matcher}

        Matches if the response has all the headers specified by the keys
        in the headers_dict, which match the corresponding matchers.
        By default the values in the dict are wrapped into the `equal_to`
        matcher.
        """
        self.register(HeadersMatcher(headers_dict))
        return self


    def with_content(self, content):
        """Adds the check for the response content

        :param content: a matcher for the content

        Matches if the content matches the given matcher. By default, this
        is wrapped into the `equal_to` matcher.
        """
        self.register(ContentMatcher(content))
        return self


    def with_cookies(self, cookies):
        """Adds the check for cookies

        :param cookies: a dictionary of {cookie_key: matcher}
        """
        self.register(CookieComponentMatcher(cookies))
        return self


def response():
    return ResponseMatcher()


def status(status_=None):
    """Matches if the item is an HttpResponse and has the given status.
    If no parameter is passed, matches any status.
    """
    return response().with_status(status_)


def has_content(content):
    """Matches if the item is an HttpResponse and has the given content
    """
    return response().with_content(content)


def has_headers(headers):
    """Matches if the item is an HttpResponse and has the given headers
    """
    return response().with_headers(headers)


def has_cookies(cookies):
    return response().with_cookies(cookies)
