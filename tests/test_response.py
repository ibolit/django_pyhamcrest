import pytest
from django.http import HttpResponse
from hamcrest import assert_that

from django_pyhamcrest.response import status
from tests.metamatchers import doesnt_match, matches


@pytest.fixture
def response_200():
    response = HttpResponse(status=200)
    response.write('{"Hello": "dude"}')
    response["Content-Type"] = "application/json"
    response.flush()
    return response


class TestResponseMatcher:
    def test_status_ok(self, response_200):
        assert_that(
            status(200),
            matches(response_200)
                .with_description("An HttpResponse object with status_code <200>")
        )


    def test_status_wrong(self, response_200):
        assert_that(
            status(300),
            doesnt_match(response_200)
                .with_description("An HttpResponse object with status_code <300>")
                .with_mismatch_description(
                    "Status code was: <200>.")
        )


    def test_status_ok_with_headers(self, response_200):
        assert_that(
            status(200).headers({"Content-Type": "application/json"}),
            matches(response_200)
                .with_description(
                    "An HttpResponse object with status_code <200>, with headers: \"Content-Type: 'application/json'\"."
            )
        )


    def test_wrong_status_with_wrong_headers(self, response_200):
        assert_that(
            status(300).headers({"Hello-Dude": "application/json"}),
            doesnt_match(response_200)
                .with_description(
                    "An HttpResponse object with status_code <300>, with headers: \"Hello-Dude: 'application/json'\".")
                .with_mismatch_description("Status code was: <200>. Does not contain header <Hello-Dude>.")
        )


    def test_status_ok_wrong_headers(self, response_200):
        assert_that(
            status(200).headers({"Hello-Dude": "3"}),
            doesnt_match(response_200)
                .with_mismatch_description(
                    "Does not contain header <Hello-Dude>."
                )
        )
