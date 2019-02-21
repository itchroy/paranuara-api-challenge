import tornado.escape
import tornado.ioloop
import tornado.web
import json
import sys
import os

from api.database import Database
from api.service import Service, UnknownInstanceError
from api.import_data import import_local_data
from api.endpoint import Endpoint


if __name__ == "__main__":
    try:
        # initialize database schema (SQLAlchemy)
        db = Database("hivery.db")

        # pre-process raw data files and load into database
        import_local_data(db, "data/companies.json", "data/people.json", "data/foods.json")

        # pass database to service
        service = Service(db)

        # construct the API endpoint
        endpoint = Endpoint(service)

        # start listening on the API endpoint
        endpoint.run(port_num=8888)

    except ImportError as err:
        print("data import failed because:: " + str(err))
        sys.exit(1)
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop() # note, this isn't safe
    except Exception as e:
        print("caught unexpected exception: " + str(e))
        raise e
        sys.exit(1)
