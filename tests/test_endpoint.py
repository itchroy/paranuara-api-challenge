import pytest

from api.model import Company, Person
from api.endpoint import Endpoint
from api.service import UnknownInstanceError

import tornado.web
from tornado.testing import AsyncTestCase, gen_test

import json

class ServiceMock(object):
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
            print("returning person 0")
            return self.people[person_id - 1]
        elif person_id == 5:
            raise Exception("random unexpected exception")
        return None


    def get_person_comparison(self, this_person_id, other_person_id):
        if this_person_id != 1:
            raise UnknownInstanceError("unknown person id '{}'".format(this_person_id))
        if other_person_id != 2 or other_person_id != 4:
            raise UnknownInstanceError("unknown id of other person '{}'".format(other_person_id))

        common = [ 3 ] if other_person_id != 4 else []

        return self.people[this_person_id - 1], self.people[other_person_id - 1], common


@pytest.fixture
def app():
    service = ServiceMock()
    endpoint = Endpoint(api_service=service)
    return endpoint.get_application()


@pytest.mark.gen_test()
def test_person_basic(http_server, http_client, base_url):
    response = yield http_client.fetch(base_url + "/person/1")
    assert response.code == 200
    assert response.headers.get("content-type") == "application/json; charset=UTF-8"

@pytest.mark.gen_test()
def test_company_fetch_200(http_server, http_client, base_url):
    response = yield http_client.fetch(base_url + "/company/0/employee")
    assert response.code == 200
    assert response.headers.get("content-type") == "application/json; charset=UTF-8"

@pytest.mark.gen_test()
def test_company_fetch_404(http_server, http_client, base_url):
    response = yield http_client.fetch(base_url + "/company/101/employee")
    assert response.code == 404
    #assert response.headers.get("content-type") == "application/json; charset=UTF-8"

    #response_body_json = json.loads(response.body)
    #assert "employees" in response_body_json
