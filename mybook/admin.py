from django.contrib import admin

from .models import Genre, Author, Book, UserShelf, BookOpinion


admin.site.register(Genre)
admin.site.register(Author)
admin.site.register(Book)
admin.site.register(UserShelf)
admin.site.register(BookOpinion)