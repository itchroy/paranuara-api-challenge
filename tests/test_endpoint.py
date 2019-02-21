import pytest

from api.model import Company, Person
from api.endpoint import Endpoint
from api.service import UnknownInstanceError

import tornado.web
import tornado.httpclient
from tornado.testing import AsyncTestCase, gen_test

import json


class ServiceMock(object):
    """
    Mock a `Service` object to test the endpoint with
    """

    def __init__(self):
        self.people = [
            Person(pid=1, name="Thor", age=650, address="SYD", email="thor@gmail.com", phone="+61459849686", eye_color="brown", alive=True),
            Person(pid=2, name="Ironman", age=40, address="BNE", email="ironman@gmail.com", phone="+61480123456", eye_color="brown", alive=True),
            Person(pid=3, name="CaptainAmerica", age=75, address="BNE", email="captain@gmail.com", phone="+61480123456", eye_color="brown", alive=True),
            Person(pid=4, name="Hulk", age=40, address="BNE", email="hulk@gmail.com", phone="+61480123456", eye_color="brown", alive=True)
        ]

    def get_employees_by_company_id(self, cid):
        if cid == 101:
            raise UnknownInstanceError("unknown company id '{}'".format(cid))

        return self.people

    def get_person_by_id(self, person_id):
        if person_id == 1:
            return self.people[person_id - 1]
        elif person_id == 5:
            raise Exception("random unexpected exception")
        return None

    def get_person_comparison(self, this_person_id, other_person_id):
        if this_person_id != 1:
            raise UnknownInstanceError("unknown person id '{}'".format(this_person_id))
        if other_person_id == 3:
            raise UnknownInstanceError("unknown id of other person '{}'".format(other_person_id))

        common = [ 3 ] if other_person_id == 2 else []

        return self.people[this_person_id - 1], self.people[other_person_id - 1], common


@pytest.fixture
def app():
    service = ServiceMock()
    endpoint = Endpoint(api_service=service)
    return endpoint.get_application()


@pytest.mark.gen_test()
def test_person_get_200(http_server, http_client, base_url):
    response = yield http_client.fetch(base_url + "/person/1")
    assert response.code == 200
    assert response.headers.get("content-type") == "application/json; charset=UTF-8"


@pytest.mark.gen_test()
def test_person_get_404(http_server, http_client, base_url):
    with pytest.raises(tornado.httpclient.HTTPError) as e:
        yield http_client.fetch(base_url + "/person/1001")

    assert e.value.code == 404
    assert e.value.response.headers.get("content-type") == "application/json; charset=UTF-8"
    assert e.value.response.body == b"{\"message\": \"resource not found\"}"


@pytest.mark.gen_test()
def test_company_employees_get_200(http_server, http_client, base_url):
    response = yield http_client.fetch(base_url + "/company/0/employee")
    assert response.code == 200
    assert response.headers.get("content-type") == "application/json; charset=UTF-8"


@pytest.mark.gen_test()
def test_company_employees_get_404(http_server, http_client, base_url):
    with pytest.raises(tornado.httpclient.HTTPError) as e:
        yield http_client.fetch(base_url + "/company/101/employee")

    assert e.value.code == 404
    assert e.value.response.headers.get("content-type") == "application/json; charset=UTF-8"
    assert e.value.response.body == b"{\"message\": \"resource not found\"}"


@pytest.mark.gen_test()
def test_person_comparison_get_200(http_server, http_client, base_url):
    response = yield http_client.fetch(base_url + "/person/1/compare?other_id=2")
    assert response.code == 200
    assert response.headers.get("content-type") == "application/json; charset=UTF-8"
    
    body_json = json.loads(response.body)
    assert body_json["this"]["id"] == 1
    assert body_json["other"]["id"] == 2
    assert body_json["common_friend_ids"] == [3]


@pytest.mark.gen_test()
def test_person_comparison_get_404(http_server, http_client, base_url):
    with pytest.raises(tornado.httpclient.HTTPError) as e:
        yield http_client.fetch(base_url + "/person/1/compare?other_id=3")

    assert e.value.code == 404
    assert e.value.response.headers.get("content-type") == "application/json; charset=UTF-8"
    assert e.value.response.body == b"{\"message\": \"resource not found\"}"


@pytest.mark.gen_test()
def test_person_comparison_get_404_bad_ids(http_server, http_client, base_url):
    with pytest.raises(tornado.httpclient.HTTPError) as e:
        yield http_client.fetch(base_url + "/person/1az/compare?other_id=tr3")

    assert e.value.code == 404

