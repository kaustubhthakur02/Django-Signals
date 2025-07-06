from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Author(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    biography = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    isbn = models.CharField(max_length=13, unique=True)
    pages = models.IntegerField()
    available_copies = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class BookStatistics(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE)
    total_borrows = models.IntegerField(default=0)
    current_borrowed = models.IntegerField(default=0)
    rating_sum = models.IntegerField(default=0)
    rating_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def average_rating(self):
        if self.rating_count == 0:
            return 0
        return round(self.rating_sum / self.rating_count, 2)
    
    def __str__(self):
        return f"Stats for {self.book.title}"

class BorrowRecord(models.Model):
    STATUS_CHOICES = [
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrowed_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    returned_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='borrowed')
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('book_created', 'Book Created'),
        ('book_borrowed', 'Book Borrowed'),
        ('book_returned', 'Book Returned'),
        ('book_deleted', 'Book Deleted'),
        ('user_registered', 'User Registered'),
    ]
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.timestamp}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    books_borrowed_count = models.IntegerField(default=0)
    membership_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Profile of {self.user.username}"