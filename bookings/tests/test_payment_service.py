from decimal import Decimal
from unittest.mock import Mock, patch

import pytest
from django.contrib.auth import get_user_model
from requests.exceptions import RequestException
from bookings.models import BookingRequest, LSAProfile, Parent
from bookings.services import create_payment


User = get_user_model()


@pytest.mark.django_db
@patch("bookings.services.requests.post")
def test_create_payment_success(mock_post):
    user = User.objects.create_user(
        username="paymentparent",
        password="testpass123",
    )

    parent = Parent.objects.create(
        user=user,
        phone_number="9876543210",
    )

    lsa = LSAProfile.objects.create(
        name="Payment Test LSA",
        is_active=True,
    )

    booking = BookingRequest.objects.create(
        parent=parent,
        lsa=lsa,
        start_time="2026-08-15T10:00:00+05:30",
        end_time="2026-08-15T11:00:00+05:30",
    )

    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "success": True,
        "transaction_id": "gateway_txn_123",
    }

    mock_post.return_value = mock_response

    payment = create_payment(
        booking,
        Decimal("500.00"),
    )

    assert payment is not None
    assert payment.amount == Decimal("500.00")
    assert payment.status == "pending"
    assert payment.gateway_response == {
        "success": True,
        "transaction_id": "gateway_txn_123",
    }

    mock_post.assert_called_once()
    
@pytest.mark.django_db
@patch("bookings.services.requests.post")
def test_create_payment_gateway_failure(mock_post):
    user = User.objects.create_user(
        username="failedpaymentparent",
        password="testpass123",
    )

    parent = Parent.objects.create(
        user=user,
        phone_number="9876543210",
    )

    lsa = LSAProfile.objects.create(
        name="Payment Failure LSA",
        is_active=True,
    )

    booking = BookingRequest.objects.create(
        parent=parent,
        lsa=lsa,
        start_time="2026-08-16T10:00:00+05:30",
        end_time="2026-08-16T11:00:00+05:30",
    )

    mock_post.side_effect = RequestException(
        "Payment gateway unavailable"
    )

    result = create_payment(
        booking,
        Decimal("500.00"),
    )

    assert result["success"] is False
    assert result["error"] == "Payment gateway request failed."

    mock_post.assert_called_once()