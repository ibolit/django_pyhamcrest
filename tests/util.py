import logging

from hamcrest.core.string_description import StringDescription


def assert_matches(matcher, arg, message):
    try:
        assert matcher.matches(arg), message
    except AssertionError:
        description = StringDescription()
        matcher.describe_mismatch(arg, description)
        logging.error(str(description))
        raise


def assert_does_not_match(matcher, arg, message):
    assert not matcher.matches(arg), message


def assert_description(expected, matcher):
    description = StringDescription()
    description.append_description_of(matcher)
    assert expected == str(description)


def assert_no_mismatch_description(matcher, arg):
    description = StringDescription()
    result = matcher.matches(arg, description)
    assert result, 'Precondition: Matcher should match item'
    assert '' == str(description), 'Expected no mismatch description'


def assert_mismatch_description(expected, matcher, arg):
    description = StringDescription()
    result = matcher.matches(arg, description)
    assert not result, 'Precondition: Matcher should not match item'
    assert expected == str(description)


def assert_describe_mismatch(expected, matcher, arg):
    description = StringDescription()
    matcher.describe_mismatch(arg, description)
    assert expected == str(description)
