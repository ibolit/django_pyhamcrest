"""This is some module documentation"""

from django.http import HttpResponse
from hamcrest import anything
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.helpers.wrap_matcher import wrap_matcher
from hamcrest.core.string_description import StringDescription


class ResponseMatcher(BaseMatcher):
    """HEllo. let's see if it appears in the doc"""
    def __init__(self, status_code):
        self.errors = []
        self.status = wrap_matcher(status_code)
        self.headers_ = {}
        self.content = None
        self.content_is_correct = False


    def with_headers(self, headers_dict):
        """Adds the check for headers.

        :param headers_dict: dict {key:  matcher}

        Matches if the response has all the headers specified by the keys
        in the headers_dict, which match the corresponding matchers.
        By default the values in the dict are wrapped into the `equal_to`
        matcher.
        """
        self.headers_ = {
            key: wrap_matcher(value) for key, value in headers_dict.items()
        }
        return self


    def with_content(self, content):
        """Adds the check for the response content

        :param content: a matcher for the content

        Matches if the content matches the given matcher. By default, this
        is wrapped into the `equal_to` matcher.
        """
        self.content = wrap_matcher(content)
        return self


    def with_cookies(self, cookies):
        """Adds the check for cookies

        :param cookies: a dictionary of {cookie_key: matcher}
        """
        pass


    def _matches(self, item):
        if not isinstance(item, HttpResponse):
            self.errors.append("Not an HttpResponse object")
            return False

        matches = True
        if not self.status.matches(item.status_code):
            matches = False
            self.errors.append("Status code was: <{}>".format(item.status_code))

        if self.headers_:
            for header, matcher in self.headers_.items():
                if not item.has_header(header):
                    matches = False
                    self.errors.append("Does not contain header <{}>".format(header))
                elif not matcher._matches(item[header]):
                    matches = False
                    descr = StringDescription()
                    matcher.describe_mismatch(item[header], descr)
                    self.errors.append("The value for header <{}> {}".format(
                        header, str(descr)))

        if self.content:
            self.content_is_correct = self.content._matches(item.content)
            descr = StringDescription()
            self.content.describe_mismatch(item.content, descr)
            self.errors.append("The content {}".format(str(descr)))
            matches &= self.content_is_correct

        return matches


    def describe_to(self, description):
        description.append_text(
            "An HttpResponse object with status_code {}".format(
                self.status))
        header_descr = []

        if self.headers_:
            for key, val in self.headers_.items():
                descr = StringDescription()
                val.describe_to(descr)
                header_descr.append("{}: {}".format(key, descr))
            description.append_list(", with headers: ", ". ", ".", header_descr)

        if self.content:
            description.append_text(" and content ")
            description.append_description_of(self.content)


    def describe_mismatch(self, item, mismatch_description):
        errors = ". ".join(self.errors)
        mismatch_description.append_text(errors).append_text(".")


def status(status_=None):
    """Matches if the item is an HttpResponse and has the given status.
    If no parameter is passed, matches any status.
    """
    if status_ is None:
        status_ = anything()
    return ResponseMatcher(status_)


def has_content(content):
    """Matches if the item is an HttpResponse and has the given content
    """
    return status().with_content(content)


def has_headers(headers):
    """Matches if the item is an HttpResponse and has the given headers
    """
    return status().with_headers(headers)
