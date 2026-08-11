from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import LSAProfile,Payment,PaymentStatus,BookingStatus
from .serializers import LSASearchSerializer,BookingCreateSerializer
from django.db import transaction


class LSASearchView(APIView):

    def get(self, request):
        skill = request.query_params.get("skill")

        if not skill:
            return Response(
                {"detail": "The 'skill' query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        lsas = (
            LSAProfile.objects
            .filter(
                is_active=True,
                skills__name__iexact=skill,
            )
            .prefetch_related("skills")
            .distinct()
        )

        serializer = LSASearchSerializer(lsas, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
        
class BookingCreateView(APIView):

    def post(self, request):
        serializer = BookingCreateSerializer(data=request.data)

        if serializer.is_valid():
            booking = serializer.save()

            return Response(
                BookingCreateSerializer(booking).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
        
class PaymentWebhookView(APIView):

    @transaction.atomic
    def post(self, request):
        transaction_id = request.data.get("transaction_id")
        payment_status = request.data.get("status")

        if not transaction_id or not payment_status:
            return Response(
                {
                    "detail": (
                        "transaction_id and status are required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payment = Payment.objects.select_related(
                "booking"
            ).get(
                transaction_id=transaction_id
            )
        except Payment.DoesNotExist:
            return Response(
                {"detail": "Payment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if payment_status == PaymentStatus.SUCCESS:
            payment.status = PaymentStatus.SUCCESS
            payment.booking.status = BookingStatus.CONFIRMED

        elif payment_status == PaymentStatus.FAILED:
            payment.status = PaymentStatus.FAILED
            payment.booking.status = BookingStatus.FAILED

        else:
            return Response(
                {"detail": "Invalid payment status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment.save(update_fields=["status", "modified"])
        payment.booking.save(update_fields=["status", "modified"])

        return Response(
            {
                "detail": "Payment status updated successfully.",
                "payment_status": payment.status,
                "booking_status": payment.booking.status,
            },
            status=status.HTTP_200_OK,
        )