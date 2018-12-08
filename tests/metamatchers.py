from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.string_description import StringDescription


class MetaMatcher(BaseMatcher):
    def __init__(self, item, result=True):
        self.result = result
        self.item = item
        self.match_result = None

        self.description = None
        self.wrong_description = None

        self.mismatch_description = None
        self.wrong_mismatch_description = None


    def with_description(self, description):
        self.description = description
        return self


    def with_mismatch_description(self, mismatch_description):
        self.mismatch_description = mismatch_description
        return self


    def _matches(self, matcher):
        ret = True
        self.match_result = matcher._matches(self.item)
        if self.result:
            ret &= self.match_result
        else:
            ret &= not self.match_result

        if self.description:
            descr = StringDescription()
            matcher.describe_to(descr)
            descr = str(descr)
            descr_is_correct = descr == self.description
            if not descr_is_correct:
                self.wrong_description = descr
                ret = False

        if self.mismatch_description:
            descr = StringDescription()
            matcher.describe_mismatch(self.item, descr)
            descr = str(descr)
            descr_is_correct = descr == self.mismatch_description
            if not descr_is_correct:
                self.wrong_mismatch_description = descr
                ret = False

        return ret


    def describe_to(self, description):
        description.append_text("A matcher that ")
        if not self.result:
            description.append_text("does not match ")
        else:
            description.append_text("matches ")
        description.append_text("the item.")

        if self.description:
            description.append_text(" With the description: <{}>".format(
                self.description
            ))

        if self.mismatch_description and self._mismatch_description_should_be_present():
            description.append_text(" With mismatch_description: <{}>".format(
                self.mismatch_description
            ))


    def _mismatch_description_should_be_present(self):
        return self.result == self.match_result == False


    def describe_mismatch(self, item, mismatch_description):
        if self.match_result != self.result:
            mismatch_description.append_text("The matcher ")
            if self.match_result:
                mismatch_description.append_text("matched. ")
            else:
                mismatch_description.append_text("did not match. ")
        if self.wrong_description:
            mismatch_description.append_text("The description was <{}>. ".format(
                self.wrong_description
            ))

        if (
                self.wrong_mismatch_description
                and self._mismatch_description_should_be_present()
        ):
            mismatch_description.append_text("The mismatch_description was <{}>. ".format(
                self.wrong_mismatch_description
            ))


def matches(item):
    return MetaMatcher(item)


def doesnt_match(item):
    return MetaMatcher(item, False)
