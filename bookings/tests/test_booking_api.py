from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from bookings.models import BookingRequest, LSAProfile, Parent, Skill, BookingStatus


User = get_user_model()


@pytest.mark.django_db
def test_create_booking_success():
    client = APIClient()

    user = User.objects.create_user(
        username="testparent",
        password="testpass123",
    )

    parent = Parent.objects.create(
        user=user,
        phone_number="9876543210",
    )

    skill = Skill.objects.create(
        name="Mathematics",
    )

    lsa = LSAProfile.objects.create(
        name="Test LSA",
        bio="Test LSA profile",
        is_active=True,
    )

    lsa.skills.add(skill)

    start_time = timezone.now() + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)

    url = reverse("booking-create")

    response = client.post(
        url,
        {
            "parent": parent.id,
            "lsa": lsa.id,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "notes": "Test booking",
        },
        format="json",
    )

    assert response.status_code == 201
    assert BookingRequest.objects.filter(
        parent=parent,
        lsa=lsa,
    ).exists()
    
@pytest.mark.django_db
def test_create_booking_invalid_time():
    client = APIClient()

    user = User.objects.create_user(
        username="invalidtimeparent",
        password="testpass123",
    )

    parent = Parent.objects.create(
        user=user,
        phone_number="9876543210",
    )

    lsa = LSAProfile.objects.create(
        name="Test LSA",
        bio="Test LSA profile",
        is_active=True,
    )

    start_time = timezone.now() + timedelta(days=1)
    end_time = start_time - timedelta(hours=1)

    url = reverse("booking-create")

    response = client.post(
        url,
        {
            "parent": parent.id,
            "lsa": lsa.id,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "notes": "Invalid time test",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "end_time" in response.data
    
@pytest.mark.django_db
def test_create_booking_overlapping_booking():
    client = APIClient()

    # Parent 1
    user1 = User.objects.create_user(
        username="parent1",
        password="testpass123",
    )

    parent1 = Parent.objects.create(
        user=user1,
        phone_number="9876543210",
    )

    # Parent 2
    user2 = User.objects.create_user(
        username="parent2",
        password="testpass123",
    )

    parent2 = Parent.objects.create(
        user=user2,
        phone_number="9876543211",
    )

    lsa = LSAProfile.objects.create(
        name="Test LSA",
        bio="Test LSA profile",
        is_active=True,
    )

    start_time = timezone.now() + timedelta(days=2)
    end_time = start_time + timedelta(hours=1)

    # Existing booking
    BookingRequest.objects.create(
        parent=parent1,
        lsa=lsa,
        start_time=start_time,
        end_time=end_time,
        status=BookingStatus.CONFIRMED,
    )

    # New booking overlaps existing booking
    new_start_time = start_time + timedelta(minutes=30)
    new_end_time = new_start_time + timedelta(hours=1)

    url = reverse("booking-create")

    response = client.post(
        url,
        {
            "parent": parent2.id,
            "lsa": lsa.id,
            "start_time": new_start_time.isoformat(),
            "end_time": new_end_time.isoformat(),
            "notes": "Overlapping booking test",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "already booked" in str(response.data).lower()