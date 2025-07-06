from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app1.models import Author, Book
from app1.signals import book_returned
import random

class Command(BaseCommand):
    help = 'Populate the library with sample data to test signals'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=3, help='Number of users to create')
        parser.add_argument('--books', type=int, default=8, help='Number of books to create')

    def handle(self, *args, **options):
        self.stdout.write('🚀 Starting to populate library...\n')
        
        # Create sample authors (signals will trigger)
        authors_data = [
            {'name': 'j.k. rowling', 'email': 'jk@example.com', 'biography': 'British author, best known for Harry Potter series'},
            {'name': 'george orwell', 'email': 'george@example.com', 'biography': 'English novelist and essayist'},
            {'name': 'agatha christie', 'email': 'agatha@example.com', 'biography': 'English crime novelist'},
            {'name': 'isaac asimov', 'email': 'isaac@example.com', 'biography': 'American science fiction writer'},
        ]
        
        self.stdout.write('📝 Creating authors...')
        authors = []
        for author_data in authors_data:
            author, created = Author.objects.get_or_create(
                name=author_data['name'],
                defaults=author_data
            )
            authors.append(author)
            if created:
                self.stdout.write(f'  ✅ Created author: {author.name}')
        
        # Create sample books (signals will trigger)
        books_data = [
            {'title': 'harry potter and the philosopher\'s stone', 'isbn': '9780747532699', 'pages': 223, 'copies': 3},
            {'title': '1984', 'isbn': '9780451524935', 'pages': 328, 'copies': 2},
            {'title': 'murder on the orient express', 'isbn': '9780062693662', 'pages': 256, 'copies': 1},
            {'title': 'foundation', 'isbn': '9780553293357', 'pages': 244, 'copies': 2},
            {'title': 'animal farm', 'isbn': '9780451526342', 'pages': 112, 'copies': 4},
            {'title': 'the da vinci code', 'isbn': '9780307474278', 'pages': 454, 'copies': 1},
            {'title': 'pride and prejudice', 'isbn': '9780141439518', 'pages': 432, 'copies': 2},
            {'title': 'to kill a mockingbird', 'isbn': '9780061120084', 'pages': 376, 'copies': 1},
        ]
        
        self.stdout.write('\n📚 Creating books...')
        books = []
        for i, book_data in enumerate(books_data[:options['books']]):
            author = authors[i % len(authors)]
            book, created = Book.objects.get_or_create(
                title=book_data['title'],
                defaults={
                    'author': author,
                    'isbn': book_data['isbn'],
                    'pages': book_data['pages'],
                    'available_copies': book_data['copies']
                }
            )
            books.append(book)
            if created:
                self.stdout.write(f'  ✅ Created book: {book.title}')
        
        # Create sample users (signals will trigger)
        self.stdout.write('\n👥 Creating users...')
        users_data = [
            {'username': 'alice_reader', 'email': 'alice@example.com', 'first_name': 'Alice', 'last_name': 'Johnson'},
            {'username': 'bob_bookworm', 'email': 'bob@example.com', 'first_name': 'Bob', 'last_name': 'Smith'},
            {'username': 'carol_student', 'email': 'carol@example.com', 'first_name': 'Carol', 'last_name': 'Davis'},
        ]
        
        users = []
        for user_data in users_data[:options['users']]:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    **user_data,
                    'password': 'pbkdf2_sha256$260000$test$test'  # Simple password for demo
                }
            )
            if created:
                user.set_password('demo123')  # Set proper password
                user.save()
                users.append(user)
                self.stdout.write(f'  ✅ Created user: {user.username} (password: demo123)')
        
        self.stdout.write(f'\n🎉 Successfully populated library!')
        self.stdout.write(f'📊 Summary:')
        self.stdout.write(f'  - Authors: {Author.objects.count()}')
        self.stdout.write(f'  - Books: {Book.objects.count()}')
        self.stdout.write(f'  - Users: {User.objects.count()}')
        self.stdout.write(f'\n💡 Now you can:')
        self.stdout.write(f'  - Visit http://127.0.0.1:8000/ to see the books')
        self.stdout.write(f'  - Login to admin with your superuser account')
        self.stdout.write(f'  - Login as any demo user (password: demo123)')
        self.stdout.write(f'  - Watch console output when borrowing/returning books!')