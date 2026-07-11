import json
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from .permissions import ReadOnlyOrAdmin
from .models import (
    Booking,
    BookingSeat,
    Event,
    Row,
    Seat,
    SeatCategory,
    Section,
    Show,
    Theater,
)
from .serializers import (
    BookingAdminSerializer,
    EventSectionSerializer,
    EventSerializer,
    GenerateSeatsSerializer,
    MultiBookingSerializer,
    RowDropdownSerializer,
    RowSerializerSimple,
    SeatCategorySerializer,
    SeatCreateSerializer,
    SeatSerializerSimple,
    SectionDropdownSerializer,
    SectionSerializerSimple,
    ShowDetailSerializer,
    ShowSerializer,
    TheaterDetailSerializer,
    TheaterSerializer,
)

# =============================================
#               Public APIs
# =============================================

class ShowViewSet(viewsets.ModelViewSet):
    permission_classes = [ReadOnlyOrAdmin]
    parser_classes = [MultiPartParser, FormParser]
    queryset = Show.objects.prefetch_related(
        "events"
    )

    def get_serializer_class(self):

        if self.action == "retrieve":
            return ShowDetailSerializer

        return ShowSerializer
    
class EventViewSet(viewsets.ModelViewSet):
    permission_classes = [ReadOnlyOrAdmin]
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    @action(detail=True, methods=['get'])
    def seat_map(self, request, pk=None):

        event = self.get_object()

        sections = Section.objects.filter(
            theater=event.theater
        ).prefetch_related(
            'rows__seats'
        )

        booked_seats = set(
            BookingSeat.objects.filter(
                booking__event=event,
                booking__status__in=[
                    Booking.Status.PENDING,
                    Booking.Status.CONFIRMED,
                ],
            ).values_list("seat_id", flat=True)
        )

        serializer = EventSectionSerializer(
            sections,
            many=True,
            context={
                "event": event,
                "booked_seats": booked_seats,
            },
        )

        return Response({
            'event_id': event.id,
            'event_title': event.title,
            'theater': event.theater.name,
            'sections': serializer.data
        })

class TheaterViewSet(viewsets.ModelViewSet):
    queryset = Theater.objects.all()
    serializer_class = TheaterSerializer
    permission_classes = [ReadOnlyOrAdmin]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TheaterDetailSerializer
        return TheaterSerializer

    @action(detail=True, methods=['get'])
    def seat_map(self, request, pk=None):
        theater = self.get_object()
        serializer = TheaterDetailSerializer(theater)
        return Response(serializer.data)
    
    @action(detail=True, methods=["get"])
    def sections(self, request, pk=None):
        theater = self.get_object()

        serializer = SectionDropdownSerializer(
            theater.sections.all(),
            many=True
        )

        return Response(serializer.data)
    
class SectionViewSet(viewsets.ModelViewSet):
    permission_classes = [ReadOnlyOrAdmin]
    queryset = Section.objects.all()
    serializer_class = SectionSerializerSimple

    @action(detail=True, methods=["get"])
    def rows(self, request, pk=None):
        section = self.get_object()

        serializer = RowDropdownSerializer(
            section.rows.all(),
            many=True
        )

        return Response(serializer.data)

class RowViewSet(viewsets.ModelViewSet):
    permission_classes = [ReadOnlyOrAdmin]
    queryset = Row.objects.all()
    serializer_class = RowSerializerSimple

    @action(detail=True, methods=["get"])
    def seats(self, request, pk=None):
        row = self.get_object()

        serializer = SeatSerializerSimple(
            row.seats.all(),
            many=True
        )

        return Response(serializer.data)
    
    @action(detail=True, methods=["post"])
    def generate_seats(self, request, pk=None):
        row = self.get_object()

        serializer = GenerateSeatsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        prefix = serializer.validated_data["prefix"]
        start = serializer.validated_data["start"]
        end = serializer.validated_data["end"]
        category = serializer.validated_data["category"]
        created = []
        skipped = []

        for number in range(start, end + 1):

            seat_number = f"{prefix}{number}"

            if Seat.objects.filter(
                row=row,
                seat_number=seat_number
            ).exists():

                skipped.append(seat_number)
                continue

            seat = Seat.objects.create(
                row=row,
                seat_number=seat_number,
                category=category
            )

            created.append(seat)

        return Response(
            {
                "created": len(created),
                "skipped": skipped
            },
            status=status.HTTP_201_CREATED
        )

class SeatViewSet(viewsets.ModelViewSet):
    permission_classes = [ReadOnlyOrAdmin]
    queryset = Seat.objects.all()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return SeatCreateSerializer

        return SeatSerializerSimple

class MultiBookingView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):

        data = request.data.dict()

        data["event"] = int(data["event"])

        data["attendees"] = json.loads(request.data["attendees"])

        if "owner_name" in request.data:
            data["owner_name"] = request.data["owner_name"]

        if "email" in request.data:
            data["email"] = request.data["email"]

        if "phone_number" in request.data:
            data["phone_number"] = request.data["phone_number"]

        if "image" in request.FILES:
            data["image"] = request.FILES["image"]

        serializer = MultiBookingSerializer(data=data)

        serializer.is_valid(raise_exception=True)

        booking = serializer.save()

        return Response(
            {
                "message": "Booking created successfully",
                "booking_id": booking.id,
            },
            status=status.HTTP_201_CREATED,
        )



# =============================================
#              Admin APIs
# =============================================


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingAdminSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=["patch"])
    def change_status(self, request, pk=None):
        booking = self.get_object()

        new_status = request.data.get("status")

        valid_statuses = [choice[0] for choice in Booking.Status.choices]

        if new_status not in valid_statuses:
            return Response(
                {
                    "error": "Invalid status.",
                    "allowed_statuses": valid_statuses,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.status = new_status
        booking.save(update_fields=["status"])

        return Response(
            {
                "message": "Booking status updated successfully.",
                "booking_id": booking.id,
                "status": booking.status,
            },
            status=status.HTTP_200_OK,
        )

class AdminTheaterViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = Theater.objects.all().order_by("id")
    serializer_class = TheaterSerializer
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    search_fields = [
        "name",
        "location",
    ]

    ordering_fields = [
        "id",
        "name",
    ]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TheaterDetailSerializer
        return TheaterSerializer
    
class SeatCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = SeatCategory.objects.select_related("theater")
    serializer_class = SeatCategorySerializer