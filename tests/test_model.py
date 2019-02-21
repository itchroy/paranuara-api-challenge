import pytest

from api.model import Company, Person, Food
from api.database import Database, read_scope, write_scope
from sqlalchemy.orm import joinedload # TODO: doesn't belong here - need to move this into `database`


def seed_database(db):
    c1 = Company(cid=0, name="Hivery")
    c2 = Company(cid=1, name="Acme")

    f1 = Food(id="orange", category="fruit")
    f2 = Food(id="capsicum", category="vegetable")

    p1 = Person(pid=1, name="Thor", age=65, address="SYD", email="thor@gmail.com", phone="+61459849686", eye_color="brown", alive=True)
    p2 = Person(pid=2, name="Ironman", age=40, address="BNE", email="ironman@gmail.com", phone="+61480123456", eye_color="brown", alive=True)
    p3 = Person(pid=3, name="CaptainAmerica", age=75, address="BNE", email="captain@gmail.com", phone="+61480123456", eye_color="brown", alive=True)
    p4 = Person(pid=4, name="Hulk", age=40, address="BNE", email="hulk@gmail.com", phone="+61480123456", eye_color="brown", alive=True)

    # add employees to their respective companies
    c1.employees.append(p1)
    c2.employees.append(p2)
    c2.employees.append(p3)
    c2.employees.append(p4)

    # add favourite foods
    p2.favourite_foods.append(f1)
    p2.favourite_foods.append(f2)
    p3.favourite_foods.append(f1)

    # establish friendships
    p1.befriend(p2)
    p1.befriend(p3)
    p2.befriend(p3)
    p4.befriend(p2)
    p4.befriend(p3)

    with write_scope(db) as session:
        session.add(c1)
        session.add(c2)
        session.add(p1)
        session.add(p2)
        session.add(p3)
        session.add(p4)


@pytest.fixture
def good_model_db():
    db = Database("./test_model_good.db")
    seed_database(db)
    return db


def test_model_integrity(good_model_db):
    with read_scope(good_model_db) as session:
        shane = session.query(Person).options(joinedload('friends')).options(joinedload('favourite_foods')).filter_by(pid=1).first()
        matt = session.query(Person).options(joinedload('favourite_foods')).filter_by(pid=2).first()
        kristian = session.query(Person).options(joinedload('favourite_foods')).filter_by(pid=3).first()
        ben = session.query(Person).options(joinedload('friends')).options(joinedload('favourite_foods')).filter_by(pid=4).first()

    shanes_friends = set([ f.pid for f in shane.friends ])
    bens_friends = set([ f.pid for f in ben.friends ])

    matts_favs = set([ f.id for f in matt.favourite_foods ])
    kristians_favs = set([ f.id for f in kristian.favourite_foods ])

    assert shane.company_id == 0
    assert ben.company_id == 1
    assert shanes_friends == bens_friends
    assert matts_favs == { "orange" , "capsicum"}
    assert kristians_favs == { "orange" }
