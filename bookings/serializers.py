from rest_framework import serializers
from .models import BookingRequest,BookingStatus
from .models import LSAProfile


class LSASearchSerializer(serializers.ModelSerializer):
    skills = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name",
    )

    class Meta:
        model = LSAProfile
        fields = (
            "id",
            "name",
            "bio",
            "skills",
            "is_active",
        )
        
class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingRequest
        fields = (
            "parent",
            "lsa",
            "start_time",
            "end_time",
            "notes",
        )

    def validate(self, attrs):
        start_time = attrs["start_time"]
        end_time = attrs["end_time"]
        lsa = attrs["lsa"]
        
        if start_time >= end_time:
            raise serializers.ValidationError(
                {
                    "end_time": "End time must be after start time."
                }
            )
            
        overlapping_booking = BookingRequest.objects.filter(
        lsa=lsa,
        start_time__lt=end_time,
        end_time__gt=start_time,
        status__in=[
            BookingStatus.PENDING_PAYMENT,
            BookingStatus.CONFIRMED,
        ],
        ).exists()
        
        if overlapping_booking:
          raise serializers.ValidationError(
            {
                "non_field_errors": [
                    "This LSA is already booked during the requested time."
                ]
            }
        )
        return attrs