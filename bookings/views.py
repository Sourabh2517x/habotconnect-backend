from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import LSAProfile
from .serializers import LSASearchSerializer,BookingCreateSerializer


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