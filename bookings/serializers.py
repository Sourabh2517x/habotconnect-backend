from rest_framework import serializers

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