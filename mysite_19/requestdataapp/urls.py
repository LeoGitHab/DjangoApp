from django.urls import path

from .views import process_get_view, user_form, handle_file_upload

app_name = "requestdatapp"
urlpatterns = [
    path('get/', process_get_view, name='get-view'),
    path('bio/', user_form, name='user-form'),
    path('uploads/', handle_file_upload, name='file-uploads'),
]
