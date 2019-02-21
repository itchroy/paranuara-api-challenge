import json

#
# Discover foods in people.json and generate a foods.json file.
# Requires a human to review foods.json and properly classify foods.
#

if __name__=="__main__":
    with open("people.json") as f:
        people = json.load(f)

    unique_foods = set()

    for person in people:
        favourites = person["favouriteFood"]
        for f in favourites:
            name = f.strip().lower()
            if len(name) > 0:
                unique_foods.add(name)
            else:
                print("invalid food name")

    classifier_map = { f: "classify_me" for f in unique_foods }

    with open("foods.json", 'w') as f:
        payload = json.dumps(classifier_map, sort_keys=True, indent=2)
        f.write(payload)

    print("# citizens: {}".format(len(people)))
    print(unique_foods)
