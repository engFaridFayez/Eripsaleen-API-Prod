# from django.contrib import admin

# # Register your models here.
# from django.contrib import admin
# from .models import Show, Theater, Section, Row, Seat, Booking,Event


# @admin.register(Theater)
# class TheaterAdmin(admin.ModelAdmin):
#     list_display = ['id', 'name', 'location']
#     search_fields = ['name']
# @admin.register(Show)
# class ShowAdmin(admin.ModelAdmin):
#     list_display = ['id', 'title', 'description', 'cover']
#     search_fields = ['title']
# @admin.register(Event)
# class EventAdmin(admin.ModelAdmin):
#     list_display = ['id', 'title', 'theater', 'event_date']
#     list_filter = ['theater', 'event_date']
#     search_fields = ['title']

# @admin.register(Section)
# class SectionAdmin(admin.ModelAdmin):
#     list_display = ['id', 'name', 'theater']
#     list_filter = ['theater']
#     search_fields = ['name']

# @admin.register(Row)
# class RowAdmin(admin.ModelAdmin):
#     list_display = ['id', 'section', 'row_number', 'seats_per_row']
#     list_filter = ['section']

# @admin.register(Seat)
# class SeatAdmin(admin.ModelAdmin):
#     list_display = ['id', 'row', 'seat_number']
#     list_filter = ['row']
#     search_fields = ['seat_number']

# @admin.register(Booking)
# class BookingAdmin(admin.ModelAdmin):
#     list_display = ['id', 'seat', 'user_name', 'created_at']
#     list_filter = ['created_at']
#     search_fields = ['user_name']