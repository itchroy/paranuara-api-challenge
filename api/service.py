from api.model import Company, Person
from api.database import read_scope

from sqlalchemy.orm import joinedload # TODO: doesn't belong here - need to move this into `database`


class ServiceError(Exception):
    pass

class UnknownInstanceError(ServiceError):
    """ Raised when an id is unknown """
    pass


class Service(object):
    """
    The "business layer" object responsible for querying DB and summarising for the view/handlers
    """
    def __init__(self, database):
        self.db = database

    def get_employees_by_company_id(self, cid):
        """
        Return list of persons employed by a company
        """
        employees = []
        with read_scope(self.db) as session:
            company = session.query(Company).filter_by(cid=cid).first()
            if company:
                for p in session.query(Person.pid, Person.email).filter_by(company_id=company.cid):
                    employees.append(p)
        if not company:
            raise UnknownInstanceError("unknown company id '{}'".format(cid))
        return employees


    def get_person_by_id(self, person_id):
        """
        Return person with {person_id}
        """
        person = None
        with read_scope(self.db) as session:
            # we execute a joined load with 'foods' so that favourite_foods is still available
            # after the DB session is closed/returned to connection pool
            person = session.query(Person).options(joinedload('favourite_foods')).filter_by(pid=person_id).first()
        return person


    def get_person_comparison(self, this_person_id, other_person_id):
        """
        Fetch person info and friends in common
        """
        with read_scope(self.db) as session:
            # we execute a joined load with 'person' so that friends is still available
            # after the DB session is closed/returned to connection pool
            this_person = session.query(Person).options(joinedload('friends')).filter_by(pid=this_person_id).first()
            other_person = session.query(Person).options(joinedload('friends')).filter_by(pid=other_person_id).first()

        if not this_person:
            raise UnknownInstanceError("unknown person id '{}'".format(this_person_id))
        if not other_person:
            raise UnknownInstanceError("unknown id of other person '{}'".format(other_person_id))

        # TODO: The below python set manipulation is absurdly inefficient for large datasets.
        # We can do better than this with this SQL query:
        #
        # SELECT
        #     *
        # FROM (
        #     SELECT
        #         friend_id,
        #         count(*) AS friend_count
        #     FROM
        #         friendship
        #     WHERE
        #         person_id IN (1, 2)
        #     GROUP BY
        #         friend_id
        #     ) AS friendships
        # INNER JOIN
        #     person
        # ON
        #     person.id = friendships.friend_id
        # WHERE
        #     friendships.friend_count = 2
        #     AND person.alive = True
        #
        # (need to transpose the above into the appropriate method calls for SQLAlchemy)
        this_friends = set([ f.pid for f in this_person.friends if f.alive == True and f.eye_color == "brown" ])
        other_friends = set([ f.pid for f in other_person.friends if f.alive == True and f.eye_color == "brown" ])
        common = this_friends.intersection(other_friends)

        return this_person, other_person, common
