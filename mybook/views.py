from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.views.generic import CreateView, DetailView, ListView
from .forms import UserDataChangeForm, UsernameChangeForm

from statistics import mean

from .models import Book, UserShelf, BookOpinion


def home(request):
    return render(request, 'mybook/home.html')


@login_required
def user_view(request):
    try:
        user_shelf = UserShelf.objects.get(user=request.user)
        user_opinions = BookOpinion.objects.filter(shelf=user_shelf)

        read_books = user_shelf.read_books.all()
        to_read_books = user_shelf.to_read_books.all()

        context = {
            'read_books': read_books,
            'to_read_books': to_read_books,
            'user_opinions' : user_opinions,
        }
    except:
        context = {
            'read_books': '',
            'to_read_books': '',
        }
    return render(request, 'mybook/profile.html', context)


@login_required
def delete_user(request):
    if request.method == 'POST':
        confirmation = request.POST.get('confirmation')

        if confirmation.lower() == request.user.username.lower():
            request.user.delete()
            messages.success(request, 'Your account has been successfully deleted')
            return redirect('home')

        else:
            messages.error(request, 'Invalid confirmation. Your account was not deleted')
            
    
    return render(request, 'mybook/delete_user.html')


@login_required
def user_settings(request):
    return render(request, 'mybook/setting_page.html')


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'mybook/signup.html'


class BookCreate(LoginRequiredMixin,CreateView):
    model = Book
    success_url = reverse_lazy('mybook:create_book')
    fields = ['title', 'author', 'isbn', 'genre']


class BookDetail(DetailView):
    model=Book
    context_object_name = 'book_detail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = Book.objects.get(pk=self.kwargs['pk'])

        context['genres'] = book.genre.all()
        context['opinions'] = book.get_opinions()

        ratings = [opinion.rating for opinion in context['opinions'] if opinion.rating is not None]
        context['average_rating'] = mean(ratings) if ratings else None

        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')

        if action == 'add_to_read':
            self.add_book_to_shelf('read', 'Read')
        elif action == 'add_to_to_read':
            self.add_book_to_shelf('to_read', 'To Read')
        else:
            messages.warning(request, 'Invalid action.')

        return redirect('mybook:book_detail', pk=self.kwargs['pk'])

    def add_book_to_shelf(self, status, shelf_name):
        book = self.get_object()
        user_shelf, created = UserShelf.objects.get_or_create(user=self.request.user)

        if status == 'read':
            user_shelf.read_books.add(book)

            read_book, created = BookOpinion.objects.get_or_create(
                book=book,
                shelf=user_shelf,
                defaults={'read_date': timezone.now().date(), 'review': '', 'rating': None}
            )

            review = self.request.POST.get('review')
            rating = self.request.POST.get('rating')
            read_date = self.request.POST.get('read_date')


            if review:
                read_book.review = review

            if rating:
                read_book.rating = int(rating)

            if read_date:
                read_book.read_date = read_date

            read_book.save()

            if not created:
                messages.warning(self.request, f'You have already marked "{book.title}" as read.')
            else:
                messages.success(self.request, f'Added "{book.title}" to your {shelf_name} books.')

        elif status == 'to_read':
            user_shelf.to_read_books.add(book)
            messages.success(self.request, f'Added "{book.title}" to your {shelf_name} books.')


class BookList(ListView):
    model=Book
    context_object_name = 'book_list'


class UserPasswordChangeView(PasswordChangeView):
    form_class = PasswordChangeForm


class UserDataChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = UserDataChangeForm
    template_name = 'registration/user_data_change_form.html'
    success_url = reverse_lazy('mybook:change_user_data_done')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class UserDataChangeDoneView(PasswordChangeDoneView):
    template_name = 'registration/user_data_change_done.html'


class UsernameChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = UsernameChangeForm
    template_name = 'registration/username_change_form.html'
    success_url = reverse_lazy('mybook:change_username_done')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class UsernameChangeDoneView(PasswordChangeDoneView):
    template_name = 'registration/username_change_done.html'