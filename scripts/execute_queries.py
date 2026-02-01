import requests
import json
import sys

STORE1_URL = "http://localhost:5001"
STORE2_URL = "http://localhost:5002"
ORDER_URL = "http://localhost:5003"

STORE_URLS = {
    "1": STORE1_URL,
    "2": STORE2_URL,
}


def populate_db():
    """Populate DB with the same data as pytest steps 1-7."""
    # Step 1: POST pet-types to store 1
    store1_types = [
        {"type": "Golden Retriever"},
        {"type": "Australian Shepherd"},
        {"type": "Abyssinian"},
    ]
    store1_ids = []
    for pt in store1_types:
        r = requests.post(f"{STORE1_URL}/pet-types", json=pt, timeout=10)
        assert r.status_code == 201, f"Failed to create {pt} on store1: {r.status_code} {r.text}"
        store1_ids.append(r.json()["id"])

    # Step 2: POST pet-types to store 2
    store2_types = [
        {"type": "Golden Retriever"},
        {"type": "Australian Shepherd"},
        {"type": "bulldog"},
    ]
    store2_ids = []
    for pt in store2_types:
        r = requests.post(f"{STORE2_URL}/pet-types", json=pt, timeout=10)
        assert r.status_code == 201, f"Failed to create {pt} on store2: {r.status_code} {r.text}"
        store2_ids.append(r.json()["id"])

    id_1, id_2, id_3 = store1_ids
    id_4, id_5, id_6 = store2_ids

    # Step 3: POST pets to store1, type1 (Golden Retriever)
    for pet in [{"name": "Lander", "birthdate": "14-05-2020"}, {"name": "Lanky"}]:
        r = requests.post(f"{STORE1_URL}/pet-types/{id_1}/pets", json=pet, timeout=10)
        assert r.status_code == 201, f"Failed to create pet {pet} on store1/{id_1}: {r.status_code}"

    # Step 4: POST pets to store1, type3 (Abyssinian)
    for pet in [{"name": "Muscles"}, {"name": "Junior"}]:
        r = requests.post(f"{STORE1_URL}/pet-types/{id_3}/pets", json=pet, timeout=10)
        assert r.status_code == 201, f"Failed to create pet {pet} on store1/{id_3}: {r.status_code}"

    # Step 5: POST pet to store2, type1 (Golden Retriever)
    r = requests.post(f"{STORE2_URL}/pet-types/{id_4}/pets", json={"name": "Shelly", "birthdate": "07-07-2019"}, timeout=10)
    assert r.status_code == 201

    # Step 6: POST pet to store2, type2 (Australian Shepherd)
    r = requests.post(f"{STORE2_URL}/pet-types/{id_5}/pets", json={"name": "Felicity", "birthdate": "27-11-2011"}, timeout=10)
    assert r.status_code == 201

    # Step 7: POST pets to store2, type4 (bulldog)
    for pet in [{"name": "Lazy", "birthdate": "07-08-2018"}, {"name": "Lemon", "birthdate": "27-03-2020"}]:
        r = requests.post(f"{STORE2_URL}/pet-types/{id_6}/pets", json=pet, timeout=10)
        assert r.status_code == 201

    print("DB populated successfully.")


def parse_entries(text):
    """Parse query.txt into a list of raw entry strings."""
    entries = []
    for part in text.split(";"):
        stripped = part.strip()
        if stripped:
            entries.append(stripped)
    return entries


def execute_query(entry):
    """Execute a query entry and return (status_code, payload_string)."""
    # Format: query: <store>,<query-string>
    content = entry[len("query:"):].strip()
    comma_idx = content.index(",")
    store = content[:comma_idx].strip()
    query_string = content[comma_idx + 1:].strip()

    base_url = STORE_URLS[store]
    url = f"{base_url}/pet-types?{query_string}"
    r = requests.get(url, timeout=10)

    if r.status_code == 200:
        return r.status_code, r.text
    else:
        return r.status_code, "NONE"


def execute_purchase(entry):
    """Execute a purchase entry and return (status_code, payload_string)."""
    # Format: purchase: <json>
    content = entry[len("purchase:"):].strip()
    payload = json.loads(content)
    r = requests.post(f"{ORDER_URL}/purchases", json=payload, timeout=10)

    if r.status_code == 201:
        return r.status_code, r.text
    else:
        return r.status_code, "NONE"


def main():
    print("Populating database")
    populate_db()

    print("Reading query.txt")
    with open("query.txt", "r") as f:
        text = f.read()

    entries = parse_entries(text)
    results = []

    for entry in entries:
        if entry.startswith("query:"):
            status, payload = execute_query(entry)
        elif entry.startswith("purchase:"):
            status, payload = execute_purchase(entry)
        else:
            print(f"Unknown entry type: {entry}", file=sys.stderr)
            continue
        results.append((status, payload))

    with open("response.txt", "w") as f:
        for status, payload in results:
            f.write(f"{status}\n{payload}\n;\n")


if __name__ == "__main__":
    main()
