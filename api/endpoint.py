import tornado.escape
import tornado.ioloop
import tornado.web

import signal

from api.service import UnknownInstanceError


class BaseHandler(tornado.web.RequestHandler):
    """
    Base request handler provides default response headers
    and fallback responses
    """
    def initialize(self, service):
        """
        This is how we pass models and business logic into
        all handlers.

        Alternatively, we could decouple the layers further by
        having the endpoint object emit request events to the
        inner layers.
        """
        self.service = service

    def set_default_headers(self, *args, **kwargs):
        """ Default CORS headers """
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Access-Control-Allow-Methods", "GET")

    def write_error(self, status_code, **kwargs):
        """ Override fall-back responder """
        if status_code == 400:
            self.finish({'message': 'bad parameter'})
        elif status_code == 404:
            self.finish({'message': 'resource not found'})
        elif status_code == 500:
            self.finish({'message': 'an unexpected error has occurred'})


class CompanyEmployeeHandler(BaseHandler):
    """
    Handle GET /company/{id}/employee
    """
    def get(self, id):
        try:
            employees = self.service.get_employees_by_company_id(int(id))
        except UnknownInstanceError:
            # exchange exception and catch in `BaseHandler`
            raise tornado.web.HTTPError(404)

        # respond with 200 OK and JSON list of `person`s
        payload = []
        for p in employees:
            payload.append({"pid": p.pid, "email": p.email})
        self.write({"employees": payload})


class PersonCompareHandler(BaseHandler):
    """
    Handle GET /person/{person_id}/compare?other_id={other_id}
    """
    def get(self, person_id):
        other_id = self.get_argument("other_id", None)
        if not other_id:
            # exchange exception and catch in `BaseHandler`
            raise tornado.web.HTTPError(400)

        try:
            this_person, other_person, common_friend_ids = self.service.get_person_comparison(int(person_id), int(other_id))
        except UnknownInstanceError:
            # exchange exception and catch in `BaseHandler`
            raise tornado.web.HTTPError(404)

        # TODO: choose a more elegant and concise serialization solution 
        # rather than packing this by hand
        response = {
            "this": {
                "id": this_person.pid,
                "name": this_person.name,
                "age": this_person.age,
                "address": this_person.address,
                "phone": this_person.phone
            },
            "other": {
                "id": other_person.pid,
                "name": other_person.name,
                "age": other_person.age,
                "address": other_person.address,
                "phone": other_person.phone
            },
            "common_friend_ids": list(common_friend_ids)
        }
        self.write(response)


class PersonHandler(BaseHandler):
    """
    Handle GET /person/{person_id}
    """
    def get(self, id):
        person = self.service.get_person_by_id(int(id))
        if not person:
            # exchange exception and catch in `BaseHandler`
            raise tornado.web.HTTPError(404)

        # TODO: choose a more elegant and concise serialization solution 
        # rather than packing this by hand
        response = {
            "username": person.email,
            "age": person.age,
            "fruits": [f.id for f in person.favourite_foods if f.category == "fruit"],
            "vegetables": [f.id for f in person.favourite_foods if f.category == "vegetable"]
        }
        self.write(response)


class Endpoint(object):
    """
    Wrapper for Tornado route handlers.
    """
    def __init__(self, api_service):
        self.api_service = api_service

        # create route handlers and inject the service (business logic) 
        # into them
        self.application = tornado.web.Application([
            (r"/company/([0-9]+)/employee", CompanyEmployeeHandler, {"service": self.api_service}),
            (r"/person/([0-9]+)/compare", PersonCompareHandler, {"service": self.api_service}),
            (r"/person/([0-9]+)", PersonHandler, {"service": self.api_service})
        ])

    def get_application(self):
        """ Get Tornado application object (required by pytest-tornado) """
        return self.application

    def run(self, port_num):
        """ start the tornado server """
        print("listening on port {}...".format(port_num))
        self.application.listen(port_num)
        tornado.ioloop.IOLoop.instance().start()
