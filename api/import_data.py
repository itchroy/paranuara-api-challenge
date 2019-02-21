import json

from api.model import Company, Person, Food
from api.database import write_scope, read_scope


class ImportError(Exception):
    pass


class DuplicateInstanceIdError(ImportError):
    pass


class UnknownReferenceError(ImportError):
    pass


def read_json_file(file_path_in):
    try:
        with open(file_path_in, 'r') as f:
            input_json = f.read()
        return json.loads(input_json)
    except Exception as e:
        print("failed to read json file because: " + str(e))
        raise


def load_company_data(companies_json):
    company_models_by_id = {}

    for i, company in enumerate(companies_json):
        cid = int(company["index"])

        # `Person`s reference company IDs in the range (1,100) however
        # `Company` indices/IDs are in the range (0,99). We make an assumption
        #  that company data needs to be manually-offset to align the references.
        cid += 1

        if cid in company_models_by_id:
            raise DuplicateInstanceIdError("duplicate company index ({}) seen at natural-index ({}), aborting load".format(cid, i))

        #  create and cache new instance of `Company`
        c = Company(cid=cid, name=company["company"])
        company_models_by_id[cid] = c
    
    return company_models_by_id


def load_people_data(people_json, foods_json, company_models_by_id):
    person_models_by_id = {}
    friend_ids_for_person_id = {}
    food_models_by_id = {}

    for i, person in enumerate(people_json):
        pid = int(person["index"])
        if pid in person_models_by_id:
            raise DuplicateInstanceIdError("duplicate person index ({}) seen at natural-index ({}), aborting load".format(pid, i))

        p = Person(
            pid=pid,
            name=person["name"],
            age=person["age"],
            address=person["address"],
            email=person["email"],
            phone=person["phone"],
            eye_color=person["eyeColor"],
            alive=not person["has_died"])

        # add p as employee to c
        company_id = int(person["company_id"])

        if company_id not in company_models_by_id:
            raise UnknownReferenceError("person ({}) at natural-index ({}) references an unknown company id ({}), aborting load".format(pid, i, company_id))

        company = company_models_by_id[company_id]
        company.employees.append(p)
        person_models_by_id[pid] = p

        # cache friend index references so we can form friendships in a later pass
        friend_list = person["friends"]
        friend_indicies = [ int(f["index"]) for f in friend_list if int(f["index"]) != pid ]
        friend_ids_for_person_id[pid] = friend_indicies

        # favourite foods
        favourites = person["favouriteFood"]
        for fav in favourites:
            food = None
            if fav in food_models_by_id:
                food = food_models_by_id[fav]
            else:
                category = foods_json.get(fav, None)
                if category is None:
                    raise UnknownReferenceError("unknown/uncategorised food '{}'".format(category))
                food = Food(id=fav, category=category)
            food_models_by_id[fav] = food
            p.favourite_foods.append(food)

    return person_models_by_id, friend_ids_for_person_id


def load_friendships(person_models_by_id, friends_for_person_id):
    for our_id, person_model in person_models_by_id.items():
        our_friends = set(friends_for_person_id[our_id])

        #print("friends for p({}): {}".format(our_id, our_friends))

        for friend_id in our_friends:
            their_friends = set(friends_for_person_id[friend_id])

            # only establish friendship if both persons reference each other as friends
            if our_id in their_friends and friend_id in our_friends:
                friend_model = person_models_by_id[friend_id]
                person_model.befriend(friend_model)


def write_models_to_database(database, companies, people):
    # start write transaction and submit models to database
    with write_scope(database) as session:
        for c in companies:
            session.add(c)

        for p in people:
            session.add(p)


def import_local_data(db, companies_path, people_path, foods_path):

    # load `company` models (but don't import yet)
    companies_json = read_json_file(companies_path)
    company_models_by_id = load_company_data(companies_json)

    # load `person` models
    people_json = read_json_file(people_path)
    foods_json = read_json_file(foods_path)
    person_models_by_id, friend_ids_for_person_id = load_people_data(people_json, foods_json, company_models_by_id)

    # now do a pass over all `person` models, creating `friendship` associations where applicable
    load_friendships(person_models_by_id, friend_ids_for_person_id)

    # submit all prepared models to database
    write_models_to_database(db, company_models_by_id.values(), person_models_by_id.values())

    print(" - {} companies imported".format(len(companies_json)))
    print(" - {} people imported".format(len(people_json)))

    # with read_scope(db) as session:
    #     for p in session.query(Person).filter_by(pid=0):
    #         print("{} ({}): {}".format(p.name, p.pid, [f.name for f in p.friends]))
    #         print("foods: {}".format([f.id for f in p.favourite_foods]))
