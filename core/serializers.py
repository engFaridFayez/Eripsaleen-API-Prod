from rest_framework import serializers
from .models import BookingSeat, SeatCategory, Show, Theater, Section, Row, Seat, Booking,Event
from django.db import transaction
from django.shortcuts import get_object_or_404
class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ['id', 'seat_number']

class RowSerializer(serializers.ModelSerializer):
    seats = SeatSerializer(many=True, read_only=True)

    class Meta:
        model = Row
        fields = ['id', 'row_number', 'seats_per_row', 'seats']


class SectionSerializer(serializers.ModelSerializer):
    rows = RowSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ['id', 'name', 'rows']

class EventSerializer(serializers.ModelSerializer):
    theater_name = serializers.CharField(source="theater.name", read_only=True)
    show_name = serializers.CharField(source="show.title", read_only=True)

    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'theater',
            'theater_name',
            'event_date',
            'sales_start',
            'sales_end',
            'show',
            'show_name'
        ]

class TheaterDetailSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)

    class Meta:
        model = Theater
        fields = ['id', 'name', 'location', 'sections']


# Simple Theater (list/create)
class TheaterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theater
        fields = ['id', 'name', 'location']


# Section (simple CRUD)
class SectionSerializerSimple(serializers.ModelSerializer):
    theater_name = serializers.CharField(
        source="theater.name",
        read_only=True
    )

    class Meta:
        model = Section
        fields = [
            "id",
            "theater",
            "theater_name",
            "name"
        ]


# 📏 Row (simple CRUD)
class RowSerializerSimple(serializers.ModelSerializer):
    section_name = serializers.CharField(
    source="section.name",
    read_only=True
    )
    theater_name = serializers.CharField(
        source="section.theater.name",
        read_only=True
    )
    class Meta:
        model = Row
        fields = ['id',"theater_name", 'section','section_name', 'row_number', 'seats_per_row']


# 💺 Seat (simple CRUD)
class SeatSerializerSimple(serializers.ModelSerializer):
    row_name = serializers.CharField(
        source="row.row_number",
        read_only=True
    )

    section_name = serializers.CharField(
        source="row.section.name",
        read_only=True
    )

    theater_name = serializers.CharField(
        source="row.section.theater.name",
        read_only=True
    )

    category = serializers.SerializerMethodField()

    def get_category(self, obj):
        if obj.category:
            return {
                "id": obj.category.id,
                "name": obj.category.name,
                "color": obj.category.color,
            }
        return None

    class Meta:
        model = Seat
        fields = [
            "id",
            "row",
            "row_name",
            "section_name",
            "seat_number",
            "theater_name",
            "category",
        ]
class BookingSeatAdminSerializer(serializers.ModelSerializer):
    seat_name = serializers.CharField(
        source="seat.seat_number",
        read_only=True
    )

    row = serializers.CharField(
        source="seat.row.row_number",
        read_only=True
    )

    section = serializers.CharField(
        source="seat.row.section.name",
        read_only=True
    )

    price = serializers.DecimalField(
        source="seat.category.price",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = BookingSeat
        fields = [
            "id",
            "person_name",
            "national_id",
            "seat_name",
            "row",
            "section",
            "price",
        ]
class BookingAdminSerializer(serializers.ModelSerializer):

    event_name = serializers.CharField(
        source="event.title",
        read_only=True
    )

    theater_name = serializers.CharField(
        source="event.theater.name",
        read_only=True
    )

    seats = BookingSeatAdminSerializer(
        many=True,
        read_only=True
    )


    seats_count = serializers.IntegerField(
        source="seats.count",
        read_only=True
    )

    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            "id",

            "event",
            "event_name",
            "status",

            "theater_name",

            "owner_name",

            "phone_number",

            "email",

            "image",

            "seats_count",

            "total_price",

            "created_at",

            "seats",
        ]

    def get_total_price(self, obj):
        return sum(
            seat.seat.category.price or 0
            for seat in obj.seats.all()
            if seat.seat.category
        )
class EventSeatSerializer(serializers.ModelSerializer):
    is_booked = serializers.SerializerMethodField()
    section = serializers.SerializerMethodField()
    row_number = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Seat
        fields = [
            "id",
            "seat_number",
            "is_booked",
            "section",
            "row_number",
            "category",
            "price",
        ]


    def get_category(self, obj):
        if not obj.category:
            return None

        return {
            "id": obj.category.id,
            "name": obj.category.name,
            "color": obj.category.color,
        }
        


    def get_price(self, obj):
        if not obj.category or obj.category.price is None:
            return 0

        return obj.category.price
    
    def get_is_booked(self, obj):
        booked_seats = self.context["booked_seats"]
        return obj.id in booked_seats

    def get_section(self, obj):
        return obj.row.section.name

    def get_row_number(self, obj):
        return obj.row.row_number


class EventRowSerializer(serializers.ModelSerializer):
    seats = serializers.SerializerMethodField()


    class Meta:
        model = Row
        fields = ['id', 'row_number', 'seats', 'section']

    def get_seats(self, obj):
        return EventSeatSerializer(
            obj.seats.all(),
            many=True,
            context=self.context
        ).data



class EventSectionSerializer(serializers.ModelSerializer):
    rows = EventRowSerializer(
    many=True,
    read_only=True
    )


    class Meta:
        model = Section
        fields = ['id', 'name', 'rows']

class AttendeeSerializer(serializers.Serializer):
    seat = serializers.IntegerField()
    person_name = serializers.CharField(max_length=255)
    national_id = serializers.CharField(max_length=14)

class MultiBookingSerializer(serializers.Serializer):
    event = serializers.IntegerField()

    owner_name = serializers.CharField(max_length=255)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    image = serializers.ImageField(required=False, allow_null=True)

    attendees = AttendeeSerializer(
        many=True,
        min_length=1
    )

    def create(self, validated_data):
        event_id = validated_data["event"]
        attendees = validated_data["attendees"]

        with transaction.atomic():

            event = get_object_or_404(Event, id=event_id)

            seat_ids = [a["seat"] for a in attendees]

            seats = (
                Seat.objects
                .select_for_update()
                .filter(id__in=seat_ids)
            )

            if seats.count() != len(seat_ids):
                raise serializers.ValidationError(
                    "One or more seats do not exist."
                )

            seat_map = {
                seat.id: seat
                for seat in seats
            }

            already_booked = BookingSeat.objects.filter(
                booking__event=event,
                booking__status__in=[
                    Booking.Status.PENDING,
                    Booking.Status.CONFIRMED,
                ],
                seat_id__in=seat_ids,
            )

            if already_booked.exists():
                raise serializers.ValidationError(
                    "One or more seats are already booked."
                )

            booking = Booking.objects.create(
                event=event,
                owner_name=validated_data["owner_name"],
                email=validated_data.get("email"),
                phone_number=validated_data.get("phone_number"),
                image=validated_data.get("image"),
            )

            booking_seats = []

            for attendee in attendees:
                booking_seats.append(
                    BookingSeat(
                        booking=booking,
                        seat=seat_map[attendee["seat"]],
                        person_name=attendee["person_name"],
                        national_id=attendee["national_id"],
                    )
                )

            BookingSeat.objects.bulk_create(booking_seats)

        return booking



class ShowEventSerializer(serializers.ModelSerializer):
    theater = serializers.StringRelatedField()

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "theater",
            "event_date"
        ]

class ShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Show
        fields = [
            "id",
            "title",
            "description",
            "cover"
        ]

class ShowDetailSerializer(serializers.ModelSerializer):

    events = ShowEventSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Show
        fields = [
            "id",
            "title",
            "description",
            "cover",
            "events"
        ]




class SectionDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ["id", "name"]

class RowDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Row
        fields = ["id", "row_number"]

class RowDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Row
        fields = ["id", "row_number"]




class GenerateSeatsSerializer(serializers.Serializer):
    prefix = serializers.CharField(max_length=10)
    start = serializers.IntegerField(min_value=1)
    end = serializers.IntegerField(min_value=1)
    category = serializers.PrimaryKeyRelatedField(
        queryset=SeatCategory.objects.all()
    )
    def validate(self, data):
        if data["start"] > data["end"]:
            raise serializers.ValidationError(
                "Start number must be less than or equal to End number."
            )

        return data
    





class SeatCategorySerializer(serializers.ModelSerializer):
    seats_count = serializers.SerializerMethodField()

    class Meta:
        model = SeatCategory
        fields = [
            "id",
            "theater",
            "name",
            "color",
            "seats_count",
            "price"
        ]

    def get_seats_count(self, obj):
        return obj.seats.count()

    def validate(self, attrs):
        theater = attrs.get(
            "theater",
            getattr(self.instance, "theater", None)
        )

        name = attrs.get(
            "name",
            getattr(self.instance, "name", None)
        )

        queryset = SeatCategory.objects.filter(
            theater=theater,
            name__iexact=name
        )

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError({
                "name": "This category already exists for this theater."
            })

        return attrs
    

class SeatCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = [
            "row",
            "seat_number",
            "category",
        ]