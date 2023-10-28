from random import random

from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User

from django.contrib.auth.views import LogoutView
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView
from django.utils.translation import gettext_lazy as _, ngettext
from django.views.decorators.cache import cache_page

from .forms import UserProfileForm
from .models import Profile


class HelloView(View):
    welcome_message = _('welcome hello world !')
    def get(self, request: HttpRequest) -> HttpResponse:
        items_str = request.GET.get('items') or 0
        items = int(items_str)
        products_line = ngettext(
            'one product',
            '{count} products',
            items,
        )
        products_line = products_line.format(count=items)

        return HttpResponse(
            f'<h1>{self.welcome_message}</h1>'
            f'\n<h2>{products_line}</h2>'
        )

# class HelloView(View):
#     def get(self, request: HttpRequest) -> HttpResponse:
#         welcome_message = _('welcome hello world !')
#         return HttpResponse(f'<h1>{welcome_message}</h1>')


class EditProfilePageView(UpdateView):
    model = Profile
    fields = ['avatar']
    context_object_name = 'profile'
    template_name_suffix = '_update_form'

    def get_object(self, queryset=None):
        profile, _ = Profile.objects.get_or_create(user_id=self.kwargs['pk'])
        return profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return reverse('myauth:users-list',)

    # def get_success_url(self):
    #     return reverse(
    #         'myauth:user_detail',
    #         kwargs={'pk': self.get_object().pk},
    #     )


class AboutMeView(CreateView):
    model = Profile
    fields = 'user', 'bio', 'avatar',
    template_name = 'myauth/about-me.html'


class UsersListView(ListView):
    template_name = 'myauth/users-list.html'
    context_object_name = 'users'
    queryset = User.objects.all()


class UsersDetailsView(UserPassesTestMixin, DetailView):
    template_name = 'myauth/user_detail.html'
    queryset = User.objects.all()
    context_object_name = 'user'
    form_class = UserProfileForm

    def test_func(self):
        self.object = self.get_object()
        if self.request.user.is_staff:
            return True
        if self.request.user.pk == self.object.pk:
            return True
        return False


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'myauth/register.html'
    success_url = reverse_lazy('myauth:about-me')

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)

        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')  # or password2
        user = authenticate(
            self.request,
            username=username,
            password=password
        )

        login(request=self.request, user=user)
        return response


def login_view(request: HttpRequest):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/admin/')

        return render(request, 'myauth/login.html')

    username = request.POST['username']
    password = request.POST['password']

    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)
        return redirect('/admin/')

    return render(request, 'myauth/login.html', {'error': 'invalid login credentials'})


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect(reverse('myauth:login'))


class MyLogoutView(LogoutView):
    next_page = reverse_lazy('myauth:login')


@user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse('Cookie set')
    response.set_cookie('fizz', 'buzz', max_age=3600)
    return response


@cache_page(60 * 2)  # 2 minutes
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get('fizz', 'default value')
    return HttpResponse(f'Cookie value: {value!r} + {random()}') # !r -  to enclose meaning of 'value' in quotation marks


@permission_required('myauth.view_profile', raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session['foobar'] = 'spam eggs'
    return HttpResponse('Session set!')


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get('foobar', 'default')
    return HttpResponse(f'Session value: {value!r}')  # !r -  to enclose meaning of 'value' in quotation marks


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({'foo': 'bar', "spam": 'eggs'})
