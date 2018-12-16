from http.cookies import SimpleCookie

from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.helpers.wrap_matcher import wrap_matcher
from pyhamcrest_toolbox.multicomponent import (
    MatcherPlugin,
    MulticomponentMatcher
)
from pyhamcrest_toolbox.util import add_not_to_str, get_mismatch_description


class BooleanMorselMatcherPlugin(MatcherPlugin):
    field_name = None

    def __init__(self, *args, **kwargs):
        super().__init__()
        if args and len(args) == 1:
            self.field_value = args[0]
        elif self.field_name in kwargs:
            self.field_value = kwargs[self.field_name]


    def component_matches(self, item):
        return item[self.field_name] == self.field_value


    def describe_to(self, description):
        description.append_text(add_not_to_str(self.field_name, self.field_value))


    def describe_component_mismatch(self, item, mismatch_description):
        mismatch_description.append_text(add_not_to_str(self.field_name, item[self.field_name]))


class IsHTTPOnlyMatcher(BooleanMorselMatcherPlugin):
    field_name = "httponly"


class IsSecureMatcher(BooleanMorselMatcherPlugin):
    field_name = "secure"


class MaxAgeMatcherPlugin(MatcherPlugin):
    def __init__(self, max_age):
        super().__init__()
        self.max_age = wrap_matcher(max_age)


    def component_matches(self, item):
        return self.max_age._matches(int(item["max-age"]))


    def describe_to(self, description):
        description.append_text(" with max-age ")\
            .append_description_of(self.max_age)


    def describe_component_mismatch(self, item, mismatch_description):
        mismatch_description.append_text("max-age {}".format(
            get_mismatch_description(self.max_age, int(item["max-age"]))
        ))


class ValueMatcherPlugin(MatcherPlugin):
    def __init__(self, value):
        super().__init__()
        self.value = wrap_matcher(value)


    def component_matches(self, item):
        return self.value._matches(item.value)


    def describe_to(self, description):
        description.append_text("with value ").append_description_of(self.value)


    def describe_component_mismatch(self, item, mismatch_description):
        mismatch_description.append_text("value {}".format(
            get_mismatch_description(self.value, item.value)
        ))


class MorselMatcher(MulticomponentMatcher):
    def __init__(self, value):
        super().__init__()
        self.register(ValueMatcherPlugin(value))


    def is_secure(self, secure=True):
        self.register(IsSecureMatcher(secure))
        return self


    def is_httponly(self, httponly=True):
        self.register(IsHTTPOnlyMatcher(httponly))
        return self


    def max_age(self, max_age):
        self.register(MaxAgeMatcherPlugin(max_age))
        return self


# 'expires' (4526940488) = {str} 'Sat, 08 Dec 2018 19:37:51 GMT'
# 'path' (4502096840) = {str} '/'
# 'comment' (4512491144) = {str} ''
# 'domain' (4507044528) = {str} ''
# 'version' (4502133536) = {str} ''
# 'samesite' (4526812016) = {str} ''
# coded_value = {str} 'dude'


def morsel(value):
    return MorselMatcher(value)


class CookieMatcher(BaseMatcher):
    def __init__(self, key_morsel_dict):
        self.matchers = key_morsel_dict

        self.errors = []


    def _matches(self, cookie):
        if not isinstance(cookie, SimpleCookie):
            self.errors.append("The item is not an instance of SimpleCookie.")
            return False

        ret = True
        for key, matcher in self.matchers.items():
            if key not in cookie:
                ret = False
                self.errors.append("Does not contain key <{}>".format(key))
            elif not matcher._matches(cookie[key]):
                ret = False
                self.errors.append(
                    "{}: {}".format(key, get_mismatch_description(
                        matcher, cookie[key])))
        return ret


    def describe_to(self, description):
        description.append_text(
            "A SimpleCookie object with: ")
        for key, m in self.matchers.items():
            description.append_text(key).append_text(":: ").append_description_of(m)

    def describe_mismatch(self, item, mismatch_description):
        mismatch_description.append_list("", ". ", "", self.errors)


def wrap_morsel_matcher(value):
    if not isinstance(value, MorselMatcher):
        value = morsel(value)
    return value


def cookie(key_morselmatcher_dct=None, **kwargs):
    if key_morselmatcher_dct is not None:
        if not isinstance(key_morselmatcher_dct, dict):
            raise ValueError("If the first artument is passed, it must be a dict")
        base_dct = {
            key: wrap_morsel_matcher(value)
            for key, value in key_morselmatcher_dct.items()
        }
    else:
        base_dct = {}
    for key, value in kwargs.items():
        base_dct[key] = wrap_morsel_matcher(value)

    return CookieMatcher(key_morselmatcher_dct)
