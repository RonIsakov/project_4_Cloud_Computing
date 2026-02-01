import requests
import pytest

STORE1_URL = "http://localhost:5001"
STORE2_URL = "http://localhost:5002"

# --- Pet Type Payloads ---
PET_TYPE1 = {"type": "Golden Retriever"}
PET_TYPE2 = {"type": "Australian Shepherd"}
PET_TYPE3 = {"type": "Abyssinian"}
PET_TYPE4 = {"type": "bulldog"}

# --- Expected Validation Values ---
PET_TYPE1_VAL ={
    "type": "Golden Retriever",
    "family": "Canidae",
    "genus": "Canis",
    "attributes": [],
    "lifespan": 12
}
PET_TYPE2_VAL = {
    "type": "Australian Shepherd",
    "family": "Canidae",
    "genus": "Canis",
    "attributes": ["Loyal", "outgoing", "and", "friendly"],
    "lifespan": 15
}

PET_TYPE3_VAL = {
    "type": "Abyssinian",
    "family": "Felidae",
    "genus": "Felis",
    "attributes": ["Intelligent", "and", "curious"]
}

PET_TYPE4_VAL = {
    "type": "bulldog",
    "family": "Canidae",
    "genus": "Canis",
    "attributes": ["Gentle", "calm", "and", "affectionate"],
}

# --- Pet Payloads ---
PET1_TYPE1 = {"name": "Lander", "birthdate": "14-05-2020"}
PET2_TYPE1 = {"name": "Lanky"}
PET3_TYPE1 = {"name": "Shelly", "birthdate": "07-07-2019"}
PET4_TYPE2 = {"name": "Felicity", "birthdate": "27-11-2011"}
PET5_TYPE3 = {"name": "Muscles"}
PET6_TYPE3 = {"name": "Junior"}
PET7_TYPE4 = {"name": "Lazy", "birthdate": "07-08-2018"}
PET8_TYPE4 = {"name": "Lemon", "birthdate": "27-03-2020"}

# Store IDs returned from POST requests
ids = {}


class TestPetStore:
    """Tests run in order — each test depends on prior tests populating ids."""

    # --- Tests 1-2: POST pet-types ---

    def test_01_post_pet_types_store1(self):
        """POST PET_TYPE1, PET_TYPE2, PET_TYPE3 to store #1."""
        payloads = [PET_TYPE1, PET_TYPE2, PET_TYPE3]
        vals = [PET_TYPE1_VAL, PET_TYPE2_VAL, PET_TYPE3_VAL]
        returned_ids = []

        for payload, val in zip(payloads, vals):
            resp = requests.post(f"{STORE1_URL}/pet-types",
                                 json=payload, timeout=10)
            assert resp.status_code == 201, f"Expected 201, got {resp.status_code}"
            data = resp.json()
            assert "id" in data
            returned_ids.append(data["id"])
            assert data["family"] == val["family"]
            assert data["genus"] == val["genus"]

        # All IDs must be unique
        assert len(set(returned_ids)) == 3
        ids["id_1"] = returned_ids[0]
        ids["id_2"] = returned_ids[1]
        ids["id_3"] = returned_ids[2]

    def test_02_post_pet_types_store2(self):
        """POST PET_TYPE1, PET_TYPE2, PET_TYPE4 to store #2."""
        payloads = [PET_TYPE1, PET_TYPE2, PET_TYPE4]
        vals = [PET_TYPE1_VAL, PET_TYPE2_VAL, PET_TYPE4_VAL]
        returned_ids = []

        for payload, val in zip(payloads, vals):
            resp = requests.post(f"{STORE2_URL}/pet-types",
                                 json=payload, timeout=10)
            assert resp.status_code == 201, f"Expected 201, got {resp.status_code}"
            data = resp.json()
            assert "id" in data
            returned_ids.append(data["id"])
            assert data["family"] == val["family"]
            assert data["genus"] == val["genus"]

        assert len(set(returned_ids)) == 3
        ids["id_4"] = returned_ids[0]
        ids["id_5"] = returned_ids[1]
        ids["id_6"] = returned_ids[2]

    # --- Tests 3-4: POST pets to store #1 ---

    def test_03_post_pets_store1_type1(self):
        """POST PET1_TYPE1, PET2_TYPE1 to pet-types/{id_1}/pets on store #1."""
        for pet in [PET1_TYPE1, PET2_TYPE1]:
            resp = requests.post(
                f"{STORE1_URL}/pet-types/{ids['id_1']}/pets",
                json=pet, timeout=10)
            assert resp.status_code == 201

    def test_04_post_pets_store1_type3(self):
        """POST PET5_TYPE3, PET6_TYPE3 to pet-types/{id_3}/pets on store #1."""
        for pet in [PET5_TYPE3, PET6_TYPE3]:
            resp = requests.post(
                f"{STORE1_URL}/pet-types/{ids['id_3']}/pets",
                json=pet, timeout=10)
            assert resp.status_code == 201

    # --- Tests 5-7: POST pets to store #2 ---

    def test_05_post_pets_store2_type1(self):
        """POST PET3_TYPE1 to pet-types/{id_4}/pets on store #2."""
        resp = requests.post(
            f"{STORE2_URL}/pet-types/{ids['id_4']}/pets",
            json=PET3_TYPE1, timeout=10)
        assert resp.status_code == 201

    def test_06_post_pets_store2_type2(self):
        """POST PET4_TYPE2 to pet-types/{id_5}/pets on store #2."""
        resp = requests.post(
            f"{STORE2_URL}/pet-types/{ids['id_5']}/pets",
            json=PET4_TYPE2, timeout=10)
        assert resp.status_code == 201

    def test_07_post_pets_store2_type4(self):
        """POST PET7_TYPE4, PET8_TYPE4 to pet-types/{id_6}/pets on store #2."""
        for pet in [PET7_TYPE4, PET8_TYPE4]:
            resp = requests.post(
                f"{STORE2_URL}/pet-types/{ids['id_6']}/pets",
                json=pet, timeout=10)
            assert resp.status_code == 201

    # --- Test 8: GET pet-type ---

    def test_08_get_pet_type2_store1(self):
        """GET /pet-types/{id_2} on store #1. Validate all PET_TYPE2_VAL fields."""
        resp = requests.get(
            f"{STORE1_URL}/pet-types/{ids['id_2']}", timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        for key, value in PET_TYPE2_VAL.items():
            assert data[key] == value, f"Field '{key}': expected {value}, got {data[key]}"

    # --- Test 9: GET pets ---

    def test_09_get_pets_type4_store2(self):
        """GET /pet-types/{id_6}/pets on store #2. Validate PET7 and PET8."""
        resp = requests.get(
            f"{STORE2_URL}/pet-types/{ids['id_6']}/pets", timeout=10)
        assert resp.status_code == 200
        pets = resp.json()
        assert isinstance(pets, list)

        pet_names = [p["name"] for p in pets]
        assert "Lazy" in pet_names
        assert "Lemon" in pet_names

        assert len(pets) == 2 
        
        for pet in pets:
            if pet["name"] == "Lazy":
                assert pet["birthdate"] == "07-08-2018"
            elif pet["name"] == "Lemon":
                assert pet["birthdate"] == "27-03-2020"
            else:
                pytest.fail(f"Unexpected pet name: {pet['name']}")

        
