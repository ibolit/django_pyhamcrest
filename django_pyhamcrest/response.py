from django.http import HttpResponse
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.helpers.wrap_matcher import wrap_matcher
from hamcrest.core.string_description import StringDescription


class ResponseMatcher(BaseMatcher):
    def __init__(self, status):
        self.errors = []
        self.status = status
        self.headers_ = {}


    def headers(self, headers_dict):
        self.headers_ = {
            key: wrap_matcher(value) for key, value in headers_dict.items()
        }
        return self


    def _matches(self, item):
        if not isinstance(item, HttpResponse):
            self.errors.append("Not an HttpResponse object")
            return False

        matches = True
        if item.status_code != self.status:
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
        return matches


    def describe_to(self, description):
        description.append_text("An HttpResponse object with status_code <{}>".format(
            self.status))
        header_descr = []

        if self.headers_:
            for key, val in self.headers_.items():
                descr = StringDescription()
                val.describe_to(descr)
                header_descr.append("{}: {}".format(key, descr))
            description.append_list(", with headers: ", ". ", ".", header_descr)


    def describe_mismatch(self, item, mismatch_description):
        errors = ". ".join(self.errors)
        mismatch_description.append_text(errors).append_text(".")


def status(status_):
    return ResponseMatcher(status_)
