# Paranuara API Project

This README covers:

1. Overview of API
2. Prerequisites & Setup
3. Running the API
4. Testing
5. REST API Documentation

Suggestion: For best viewing of tables in this document, use the 'Open Preview' right-click option on this MD file in VSCode, or just on GitHub.

# Overview of the implementation

This app uses the `SQLAlchemy` ORM with an SQLite database as the backing store. For the endpoint implementation, the [Tornado](https://www.tornadoweb.org/en/stable/) framework is used.

Tornado is also simple-to-use high-performance networking library. However in this solution, the HTTP handlers run synchronously as they are blocked by default by SQLAlchemy session. I hope that's acceptable for this solution as the overall architecture isn't defined for scalability anyhow and lacks features such as caching or the use of `asyncio` or another suitable async wrapper for Tornado to allowing yielding of CPU during database fetches (so other incoming requests can be serviced).

## Notes:

- As there was no formal schema defined for the reference JSON files, the functions in `import_data.py` assume a structure as seen in the supplied JSON files.

- Foods discovered in `people.json` must be classified prior to use and the script `data/gen_unique_foods.py` will extract unique discovered food names, generate a `foods.json` file which needs to be reviewed by a human. The map that it provides could easily have been hard-coded into the source code but since it was stated in the requirements that alternate `people.json` files could be used, I decided to make the mapping easily extensible via a new file should a `people.json` be used that possibly introduces new foods.

- The `companies.json` file is "cleaned" during load (in `import_data.py:40`). I noticed that company `index` starts from a zero-based index while the `company_id` in people.json appears to start index from '1' onwards. To align the references, the `index` of a company is offset by +1 before database load. This way all persons in `people.json` reference valid companies.

- If a friendship isn't bi-directional, i.e. if person `a` references person `b` as a friend but not vice-versa, then a friendship doesn't exists and isn't created in the model. This means that a large number of people don't have mutual friends in the supplied dataset, and even less who have mutual **brown-eyed** and **alive** friends.

- As no concept of a user was required, there is no authentication/authorization implemented.

Directory layout:
```
├── api
│   ├── database.py                 <-- Database/SQLAlchemy
│   ├── endpoint.py                 <-- Tornado request handlers
│   ├── import_data.py              <-- utilities to load JSON files into database
│   ├── model.py                    <-- SQLAlchemy models
│   └── service.py                  <-- API "business logic"
├── data
│   ├── companies.json
│   ├── foods.json
│   ├── gen_unique_foods.py         <-- Reads people.json and generates foods.json
│   └── people.json
├── main.py                         <-- Server entry-point
├── README.md
├── requirements.txt
└── tests                           <-- pytest unit tests
```

# Prerequisites & Setup

These instructions were tested on Ubuntu 18.04 which pre-installs Python 3, and also on MacOS 10.14 (Mojave).

1. Verify the version of `python3`:

```
$ python3 -V
```

If you see output similar to below, then proceed.
```
Python 3.6.7
```

2. Install `venv`

```
sudo apt install python3-venv
```

3. Enter project directory and create a virtual environment:

```
$ cd hivery-challenge
$ python3 -m venv env
```

4. Activate the environment

```
$ source env/bin/activate
```

5. Install dependencies

```
(env) $ pip install -r requirements.txt
```

You may see errors regarding failures to build wheels for `tornado` and `SQLAlchemy`. Please ignore these.

# Running the API

Server entry-point is in `{project_root}/main.py`. Run with:
```
$ cd {project_root}
$ python3 main.py
```

# Tests

Run tests with:
```
pytest -W ignore::DeprecationWarning
```

Note: Deprecation warnings are disabled as the ones that do occur are related to the `pytest-tornado` plugin and don't obscure testing.


# REST API Documentation

The API consists of 3 endpoints.

## (1) GET /company/{id}/employee

**Get list of all employees at a company**

### Request:

| Field | Type | Description |
| ------ | --- | ----------- |
| `id` | String(Integer) | primary key of company |

Example:
```
curl -i 127.0.0.1:8888/company/5/employee
```

### Response:

Possible HTTP Status:

| Status | Description |
| ------ | ----------- |
| 200 OK | ... |
| 400 Bad Request | ... |
| 404 Not Found | ... |
| 500 Internal Server Error | ... |

Schema:

Person Object:

| field | type | description |
| ------ | ----------- | ---- |
| `pid` | Integer | ... |
| `email` | String | ... |

Response Object:

| field | type | description |
| ------ | ----------- | ---- |
| `employees` | List(`Person`) | Employees list |

Example (real response from supplied dataset):
```
HTTP/1.1 200 OK
Server: TornadoServer/5.1.1
Content-Type: application/json; charset=UTF-8
Date: Thu, 21 Feb 2019 01:00:06 GMT
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: x-requested-with
Access-Control-Allow-Methods: GET
Etag: "01129bf5f067f05bef534dcf77cc59fe6038eabf"
Content-Length: 712

{"employees": [{"pid": 19, "email": "cortezfuentes@earthmark.com"}, {"pid": 161, "email": "nicholsonharrell@earthmark.com"}, {"pid": 181, "email": "colliermeadows@earthmark.com"}, {"pid": 205, "email": "henriettamccall@earthmark.com"}, {"pid": 230, "email": "hooperburke@earthmark.com"}, {"pid": 271, "email": "eleanorbarrett@earthmark.com"}, {"pid": 348, "email": "veracantrell@earthmark.com"}, {"pid": 474, "email": "jonesguzman@earthmark.com"}, {"pid": 526, "email": "tracybailey@earthmark.com"}, {"pid": 535, "email": "mcphersontorres@earthmark.com"}, {"pid": 600, "email": "mejiacarrillo@earthmark.com"}, {"pid": 817, "email": "wardcobb@earthmark.com"}, {"pid": 955, "email": "duranparsons@earthmark.com"}]}
```

# (2) GET /person/{this_id}/compare?other_id={their_id}

**Fetch comparison report for two people. List friends in common who **have brown eyes** and are **alive**.**

## Request:

| Field | Type | Description |
| ------ | --- | ----------- |
| `this_id` | String(Integer) | Person `a` GUID |
| `their_id` | String(Integer) | Person `b` GUID |

Example:
```
curl -i 127.0.0.1:8888/person/6/compare?other_id=7
```

## Response:

Possible HTTP Status:

| Status | Description |
| ------ | ----------- |
| 200 OK | ... |
| 400 Bad Request | ... |
| 404 Not Found | ... |
| 500 Internal Server Error | ... |

Schema:

Person Object:

| field | type | description |
| ------ | ----------- | ---- |
| `id` | Integer | ... |
| `name` | String | ... |
| `age` | Integer | .. |
| `address` | String | ... |
| `phone` | String | ... |

Response Object:

| field | type | description |
| ------ | ----------- | ---- |
| `this` | Person | info for person `a` |
| `other` | Person | info for person `b` |
| `common_friend_ids` | List(`Person.id`) | Shared **brown-eyed** and **alive** friends  |


Example (real response from supplied dataset):
```
HTTP/1.1 200 OK
Server: TornadoServer/5.1.1
Content-Type: application/json; charset=UTF-8
Date: Thu, 21 Feb 2019 02:30:59 GMT
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: x-requested-with
Access-Control-Allow-Methods: GET
Etag: "6c4e337eabb98606781af7373b1c71ba21f38f6a"
Content-Length: 307

{"this": {"id": 6, "name": "Cote Booth", "age": 26, "address": "394 Loring Avenue, Salvo, Maryland, 9396", "phone": "+1 (842) 598-3525"}, "other": {"id": 7, "name": "Stark Cole", "age": 29, "address": "429 Estate Road, Vallonia, Michigan, 5093", "phone": "+1 (847) 479-3112"}, "common_friend_ids": [16, 13]}
```

## (3) GET /person/{id}

**For one person, provide a list of fruits and vegetables that they like.**

### Request:

| Field | Type | Description |
| ------ | --- | ----------- |
| `id` | String(Integer) | Person ID (the field `index` from JSON dataset) |

Example:
```
curl -i 127.0.0.1:8888/person/5
```

### Response:

Possible HTTP Statuses:

| Status | Description |
| ------ | ----------- |
| 200 OK | ... |
| 400 Bad Request | ... |
| 404 Not Found | ... |
| 500 Internal Server Error | ... |

Example (from supplied dataset):

```
HTTP/1.1 200 OK
Server: TornadoServer/5.1.1
Content-Type: application/json; charset=UTF-8
Date: Thu, 21 Feb 2019 00:35:21 GMT
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: x-requested-with
Access-Control-Allow-Methods: GET
Etag: "59451f24e8734fd3dec68157c3c0c6cc7ea9ccae"
Content-Length: 127

{"username": "gracekelly@earthmark.com", "age": 24, "fruits": ["strawberry"], "vegetables": ["cucumber", "beetroot", "carrot"]}
```
