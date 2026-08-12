import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from bookings.models import LSAProfile, Skill

@pytest.mark.django_db
def test_lsa_search_by_skill():
    client = APIClient()

    mathematics = Skill.objects.create(
        name="Mathematics",
    )

    english = Skill.objects.create(
        name="English",
    )

    matching_lsa = LSAProfile.objects.create(
        name="Math LSA",
        bio="Teaches mathematics",
        is_active=True,
    )
    matching_lsa.skills.add(mathematics)

    inactive_lsa = LSAProfile.objects.create(
        name="Inactive LSA",
        bio="Inactive profile",
        is_active=False,
    )
    inactive_lsa.skills.add(mathematics)

    different_skill_lsa = LSAProfile.objects.create(
        name="English LSA",
        bio="Teaches English",
        is_active=True,
    )
    different_skill_lsa.skills.add(english)

    url = reverse("lsa-search")

    response = client.get(
        url,
        {"skill": "Mathematics"},
    )

    assert response.status_code == 200

    returned_names = [
        lsa["name"]
        for lsa in response.data
    ]

    assert "Math LSA" in returned_names
    assert "Inactive LSA" not in returned_names
    assert "English LSA" not in returned_names