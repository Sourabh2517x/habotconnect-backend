import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse

from bookings.models import (
    BookingRequest,
    BookingStatus,
    LSAProfile,
    Parent,
    Payment,
    PaymentStatus,
)


User = get_user_model()


@pytest.mark.django_db
def test_payment_webhook_success():
    client = APIClient()

    user = User.objects.create_user(
        username="webhookparent",
        password="testpass123",
    )

    parent = Parent.objects.create(
        user=user,
        phone_number="9876543210",
    )

    lsa = LSAProfile.objects.create(
        name="Webhook Test LSA",
        is_active=True,
    )

    booking = BookingRequest.objects.create(
        parent=parent,
        lsa=lsa,
        start_time="2026-08-17T10:00:00+05:30",
        end_time="2026-08-17T11:00:00+05:30",
        status=BookingStatus.PENDING_PAYMENT,
    )

    payment = Payment.objects.create(
        booking=booking,
        transaction_id="webhook_txn_123",
        amount=500,
        currency="INR",
        status=PaymentStatus.PENDING,
    )

    url = reverse("payment-webhook")

    response = client.post(
        url,
        {
            "transaction_id": payment.transaction_id,
            "status": "success",
        },
        format="json",
    )

    assert response.status_code == 200

    payment.refresh_from_db()
    booking.refresh_from_db()

    assert payment.status == PaymentStatus.SUCCESS
    assert booking.status == BookingStatus.CONFIRMED
    
@pytest.mark.django_db
def test_payment_webhook_failure():
    client = APIClient()

    user = User.objects.create_user(
        username="webhookfailureparent",
        password="testpass123",
    )

    parent = Parent.objects.create(
        user=user,
        phone_number="9876543210",
    )

    lsa = LSAProfile.objects.create(
        name="Webhook Failure LSA",
        is_active=True,
    )

    booking = BookingRequest.objects.create(
        parent=parent,
        lsa=lsa,
        start_time="2026-08-18T10:00:00+05:30",
        end_time="2026-08-18T11:00:00+05:30",
        status=BookingStatus.PENDING_PAYMENT,
    )

    payment = Payment.objects.create(
        booking=booking,
        transaction_id="webhook_failed_txn_123",
        amount=500,
        currency="INR",
        status=PaymentStatus.PENDING,
    )

    url = reverse("payment-webhook")

    response = client.post(
        url,
        {
            "transaction_id": payment.transaction_id,
            "status": "failed",
        },
        format="json",
    )

    assert response.status_code == 200

    payment.refresh_from_db()
    booking.refresh_from_db()

    assert payment.status == PaymentStatus.FAILED
    assert booking.status == BookingStatus.FAILED