from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from django.dispatch import receiver, Signal
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Book, BookStatistics, BorrowRecord, ActivityLog, UserProfile, Author

# Custom signal for book return
book_returned = Signal()

# =======================
# USER RELATED SIGNALS
# =======================

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile when a new user is created"""
    if created:
        UserProfile.objects.create(user=instance)
        # Log the activity
        ActivityLog.objects.create(
            action='user_registered',
            description=f"New user '{instance.username}' registered in the system",
            user=instance
        )
        print(f"✅ Profile created for user: {instance.username}")

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save user profile when user is saved"""
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()

# =======================
# BOOK RELATED SIGNALS
# =======================

@receiver(post_save, sender=Book)
def create_book_statistics(sender, instance, created, **kwargs):
    """Create statistics record when a new book is created"""
    if created:
        BookStatistics.objects.create(book=instance)
        
        # Log the activity
        ActivityLog.objects.create(
            action='book_created',
            description=f"New book '{instance.title}' by {instance.author.name} added to library"
        )
        print(f"📚 Book statistics created for: {instance.title}")

@receiver(pre_save, sender=Book)
def validate_book_data(sender, instance, **kwargs):
    """Clean and validate book data before saving"""
    # Auto-format title to title case
    instance.title = instance.title.title()
    
    # Ensure ISBN is clean (remove spaces and hyphens)
    instance.isbn = instance.isbn.replace(' ', '').replace('-', '')
    
    # Ensure we don't have negative copies
    if instance.available_copies < 0:
        instance.available_copies = 0
        
    print(f"📝 Book data validated for: {instance.title}")

@receiver(post_delete, sender=Book)
def cleanup_book_deletion(sender, instance, **kwargs):
    """Clean up when a book is deleted"""
    # Log the deletion
    ActivityLog.objects.create(
        action='book_deleted',
        description=f"Book '{instance.title}' by {instance.author.name} was removed from library"
    )
    
    # Note: BookStatistics will be auto-deleted due to CASCADE
    print(f"🗑️ Book '{instance.title}' deleted and cleaned up")

# =======================
# BORROW RECORD SIGNALS
# =======================

@receiver(post_save, sender=BorrowRecord)
def handle_book_borrow(sender, instance, created, **kwargs):
    """Handle actions when a book is borrowed"""
    if created and instance.status == 'borrowed':
        # Update book statistics
        stats, _ = BookStatistics.objects.get_or_create(book=instance.book)
        stats.total_borrows += 1
        stats.current_borrowed += 1
        stats.save()
        
        # Update user profile
        profile, _ = UserProfile.objects.get_or_create(user=instance.user)
        profile.books_borrowed_count += 1
        profile.save()
        
        # Decrease available copies
        book = instance.book
        if book.available_copies > 0:
            book.available_copies -= 1
            book.save()
        
        # Log the activity
        ActivityLog.objects.create(
            action='book_borrowed',
            description=f"'{instance.book.title}' borrowed by {instance.user.username}",
            user=instance.user
        )
        
        print(f"📖 Book '{instance.book.title}' borrowed by {instance.user.username}")

@receiver(pre_save, sender=BorrowRecord)
def set_due_date(sender, instance, **kwargs):
    """Set due date to 14 days from borrow date if not set"""
    if not instance.due_date and instance.borrowed_at:
        instance.due_date = instance.borrowed_at + timedelta(days=14)

# =======================
# CUSTOM SIGNAL HANDLERS
# =======================

@receiver(book_returned)
def handle_book_return(sender, borrow_record, returned_by, **kwargs):
    """Handle book return through custom signal"""
    # Update borrow record
    borrow_record.status = 'returned'
    borrow_record.returned_at = timezone.now()
    borrow_record.save()
    
    # Update book statistics
    stats = borrow_record.book.bookstatistics
    stats.current_borrowed = max(0, stats.current_borrowed - 1)
    stats.save()
    
    # Increase available copies
    book = borrow_record.book
    book.available_copies += 1
    book.save()
    
    # Log the activity
    ActivityLog.objects.create(
        action='book_returned',
        description=f"'{borrow_record.book.title}' returned by {borrow_record.user.username}",
        user=borrow_record.user
    )
    
    print(f"📥 Book '{borrow_record.book.title}' returned by {borrow_record.user.username}")

# =======================
# AUTHOR RELATED SIGNALS
# =======================

@receiver(pre_save, sender=Author)
def format_author_name(sender, instance, **kwargs):
    """Format author name to title case"""
    instance.name = instance.name.title()
    print(f"👤 Author name formatted: {instance.name}")