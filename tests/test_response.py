import pytest
from django.http import HttpResponse, SimpleCookie
from hamcrest import assert_that
from pyhamcrest_metamatchers.metamatchers import matches, doesnt_match

from django_pyhamcrest.matchers.cookie import morsel, cookie
from django_pyhamcrest.matchers.response import status, has_headers



@pytest.fixture
def response_200():
    response = HttpResponse(status=200)
    response.write('{"Hello": "dude"}')
    response["Content-Type"] = "application/json"
    response.set_cookie("hello", "dude", max_age=40, secure=True, httponly=True)
    response.set_cookie("someting", "moves", max_age=499)
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
            status(200).with_headers({"Content-Type": "application/json"}),
            matches(response_200)
                .with_description(
                    "An HttpResponse object with status_code <200>, "
                    "with headers: \"Content-Type: 'application/json'\".")
        )


    def test_wrong_status_with_wrong_headers(self, response_200):
        assert_that(
            status(300).with_headers({"Hello-Dude": "application/json"}),
            doesnt_match(response_200)
                .with_description(
                    "An HttpResponse object with status_code <300>, "
                    "with headers: \"Hello-Dude: 'application/json'\".")
                .with_mismatch_description(
                    "Status code was: <200>. Does not contain header <Hello-Dude>.")
        )


    def test_status_ok_wrong_headers(self, response_200):
        assert_that(
            status(200).with_headers({"Hello-Dude": "3"}),
            doesnt_match(response_200)
                .with_mismatch_description(
                    "Does not contain header <Hello-Dude>.")
        )


    def test_response_content(self, response_200):
        assert_that(
            status().with_content(b'{"Hello": "dude"}'),
            matches(response_200)
                .with_description(
                    "An HttpResponse object with status_code ANYTHING "
                    "and content <b'{\"Hello\": \"dude\"}'>")
        )


    def test_response_wrong_content(self, response_200):
        assert_that(
            status().with_content('{"i": "Dude"}'),
            doesnt_match(response_200)
                .with_mismatch_description(
                    "The content was <b'{\"Hello\": \"dude\"}'>.")
        )


    def test_only_headers(self, response_200):
        assert_that(
            has_headers({"Hello-Dude": "3"}),
            doesnt_match(response_200)
                .with_mismatch_description(
                    "Does not contain header <Hello-Dude>.")
        )


    def test_only_content(self, response_200):
        assert_that(
            status().with_content('{"i": "Dude"}'),
            doesnt_match(response_200)
                .with_mismatch_description(
                    "The content was <b'{\"Hello\": \"dude\"}'>.")
        )


class TestCookieMatcher:
    @pytest.fixture
    def default_cookie(self):
        cookie = SimpleCookie(
            "hello=dude; "
            "expires=Sat, 08 Dec 2018 19:51:39 GMT; "
            "HttpOnly; "
            "Max-Age=40; "
            "Path=/; "
            "Secure"
        )
        return cookie


    def test_e(self, default_cookie):
        assert_that(default_cookie, cookie(
            {
                "hello": morsel("duded").is_secure().is_httponly(False).max_age(40)
            }
        ))

