from hamcrest.core.base_matcher import BaseMatcher


class ZerothMatcher(BaseMatcher):
    def __init__(self, expected):
        self.expected = expected


    def _matches(self, item):
        return item == self.expected


    def describe_mismatch(self, item, mismatch_description):
        mismatch_description.append_text("Mismatch")


    def describe_to(self, description):
        description.append_text("Description")


def zeroth_matcher(expected):
    return ZerothMatcher(expected)
