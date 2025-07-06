from django.contrib import admin
from .models import Author, Book, BookStatistics, BorrowRecord, ActivityLog, UserProfile

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created_at']
    search_fields = ['name', 'email']

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'available_copies', 'created_at']
    list_filter = ['author', 'created_at']
    search_fields = ['title', 'isbn']

@admin.register(BookStatistics)
class BookStatisticsAdmin(admin.ModelAdmin):
    list_display = ['book', 'total_borrows', 'current_borrowed', 'average_rating']
    readonly_fields = ['book', 'total_borrows', 'current_borrowed']

@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'borrowed_at', 'due_date', 'status']
    list_filter = ['status', 'borrowed_at']
    search_fields = ['user__username', 'book__title']

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'description', 'user', 'timestamp']
    list_filter = ['action', 'timestamp']
    readonly_fields = ['action', 'description', 'user', 'timestamp']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'books_borrowed_count', 'membership_date']
    readonly_fields = ['books_borrowed_count', 'membership_date']