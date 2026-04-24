from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Infrastructure
    path('blocks/', views.block_list, name='block_list'),
    path('blocks/create/', views.block_create, name='block_create'),
    path('blocks/<int:pk>/edit/', views.block_edit, name='block_edit'),
    path('blocks/<int:pk>/delete/', views.block_delete, name='block_delete'),

    path('rooms/', views.room_list, name='room_list'),
    path('rooms/create/', views.room_create, name='room_create'),
    path('rooms/<int:pk>/edit/', views.room_edit, name='room_edit'),
    path('rooms/<int:pk>/delete/', views.RoomDeleteView.as_view(), name='room_delete'),

    # Academic
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', views.DepartmentEditView.as_view(), name='department_edit'),
    path('departments/<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department_delete'),

    path('batches/', views.batch_list, name='batch_list'),
    path('batches/create/', views.batch_create, name='batch_create'),
    path('batches/subjects/', views.batch_subjects_view, name='batch_subjects_view'),
    path('batches/upload-csv/', views.batch_subject_upload_csv, name='batch_subject_upload_csv'),
    path('batches/<int:pk>/edit/', views.batch_edit, name='batch_edit'),
    path('batches/<int:pk>/delete/', views.BatchDeleteView.as_view(), name='batch_delete'),
    path('batches/<int:pk>/', views.batch_detail, name='batch_detail'),

    path('faculty/', views.faculty_list, name='faculty_list'),
    path('faculty/create/', views.faculty_create, name='faculty_create'),
    path('faculty/upload-csv/', views.faculty_upload_csv, name='faculty_upload_csv'),
    path('faculty/<int:pk>/edit/', views.FacultyEditView.as_view(), name='faculty_edit'),
    path('faculty/<int:pk>/delete/', views.FacultyDeleteView.as_view(), name='faculty_delete'),

    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/create/', views.subject_create, name='subject_create'),
    path('subjects/upload-csv/', views.subject_upload_csv, name='subject_upload_csv'),
    path('subjects/<int:pk>/edit/', views.SubjectEditView.as_view(), name='subject_edit'),
    path('subjects/<int:pk>/delete/', views.SubjectDeleteView.as_view(), name='subject_delete'),

    path('faculty-subjects/', views.faculty_subject_list, name='faculty_subject_list'),
    path('faculty-subjects/create/', views.faculty_subject_create, name='faculty_subject_create'),
    path('faculty-subjects/upload-csv/', views.upload_faculty_subject_csv, name='upload_faculty_subject'),

    # Timetable
    path('timetable/generate/', views.generate_timetable, name='generate_timetable'),
    path('timetable/view/', views.timetable_view, name='timetable_view'),
    path('timetable/manual-entry/', views.manual_entry_create, name='manual_entry_create'),
]
