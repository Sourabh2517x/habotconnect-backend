import logging
import uuid
import requests
from .models import Payment,PaymentStatus

logger = logging.getLogger(__name__)


def create_payment(booking, amount):
    transaction_id = f"txn_{uuid.uuid4().hex[:20]}"

    payment = Payment.objects.create(
        booking=booking,
        transaction_id=transaction_id,
        amount=amount,
        currency="INR",
    )

    payload = {
        "booking_id": booking.id,
        "transaction_id": transaction_id,
        "amount": str(amount),
        "currency": payment.currency,
    }

    try:
        response = requests.post(
            "https://httpbin.org/post",
            json=payload,
            timeout=5,
        )

        response.raise_for_status()

        data = response.json()

        payment.gateway_response = data
        payment.save(update_fields=["gateway_response", "updated"])

        logger.info(
            "Payment request successful for booking %s",
            booking.id,
        )

        return payment

    except requests.exceptions.Timeout:
        logger.error(
            "Payment gateway timeout for booking %s",
            booking.id,
        )

        return payment

    except requests.exceptions.RequestException as exc:
        logger.error(
            "Payment gateway request failed for booking %s: %s",
            booking.id,
            exc,
        )
        payment.status = PaymentStatus.FAILED
        payment.gateway_response = {
        "error": "Payment gateway request failed."
        }
        payment.save(update_fields=["status", "gateway_response"])
        return payment

    except ValueError:
        logger.error(
            "Invalid response from payment gateway for booking %s",
            booking.id,
        )

        return payment