from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Book, BorrowRecord, ActivityLog
from .signals import book_returned

def book_list(request):
    books = Book.objects.all().select_related('author', 'bookstatistics')
    return render(request, 'library/book_list.html', {'books': books})

@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    if book.available_copies <= 0:
        messages.error(request, 'No copies available for borrowing.')
        return redirect('book_list')
    
    # Check if user already has this book
    existing_borrow = BorrowRecord.objects.filter(
        user=request.user,
        book=book,
        status='borrowed'
    ).exists()
    
    if existing_borrow:
        messages.error(request, 'You already have this book borrowed.')
        return redirect('book_list')
    
    # Create borrow record (this will trigger signals)
    BorrowRecord.objects.create(
        user=request.user,
        book=book,
        due_date=timezone.now() + timezone.timedelta(days=14)
    )
    
    messages.success(request, f'Successfully borrowed "{book.title}"')
    return redirect('book_list')

@login_required
def return_book(request, borrow_id):
    borrow_record = get_object_or_404(
        BorrowRecord,
        id=borrow_id,
        user=request.user,
        status='borrowed'
    )
    
    # Send custom signal for book return
    book_returned.send(
        sender=None,
        borrow_record=borrow_record,
        returned_by=request.user
    )
    
    messages.success(request, f'Successfully returned "{borrow_record.book.title}"')
    return redirect('my_books')

@login_required
def my_books(request):
    borrowed_books = BorrowRecord.objects.filter(
        user=request.user,
        status='borrowed'
    ).select_related('book')
    return render(request, 'library/my_books.html', {'borrowed_books': borrowed_books})

def activity_log(request):
    activities = ActivityLog.objects.all().order_by('-timestamp')[:50]
    return render(request, 'library/activity_log.html', {'activities': activities})