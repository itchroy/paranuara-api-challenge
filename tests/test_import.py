import pytest

from api.import_data import ImportError, DuplicateInstanceIdError, UnknownReferenceError
from api.import_data import read_json_file, load_company_data, load_people_data

@pytest.fixture
def companies_with_duplicate_ids():
    companies_json = read_json_file("tests/import_companies_bad_0.json")
    return companies_json


@pytest.fixture
def people_with_unknown_company_ids_0():
    companies_json = read_json_file("tests/import_companies_good_0.json")
    people_json = read_json_file("tests/import_people_bad_0.json")
    foods_json = read_json_file("tests/import_foods_good_0.json")

    return companies_json, people_json, foods_json

@pytest.fixture
def people_with_duplicate_people_ids_0():
    companies_json = read_json_file("tests/import_companies_good_0.json")
    people_json = read_json_file("tests/import_people_bad_1.json")
    foods_json = read_json_file("tests/import_foods_good_0.json")

    return companies_json, people_json, foods_json


def test_raises_on_duplicate_company_indices(companies_with_duplicate_ids):
    with pytest.raises(DuplicateInstanceIdError):
        load_company_data(companies_with_duplicate_ids)


def test_raises_on_unknown_company_id(people_with_unknown_company_ids_0):
    company_models_by_id = load_company_data(people_with_unknown_company_ids_0[0])
    
    with pytest.raises(UnknownReferenceError):
        load_people_data(
            people_with_unknown_company_ids_0[1], 
            people_with_unknown_company_ids_0[2], 
            company_models_by_id)


def test_raises_on_duplicate_people_indices(people_with_duplicate_people_ids_0):
    company_models_by_id = load_company_data(people_with_duplicate_people_ids_0[0])
    
    with pytest.raises(DuplicateInstanceIdError):
        load_people_data(
            people_with_duplicate_people_ids_0[1], 
            people_with_duplicate_people_ids_0[2], 
            company_models_by_id)





