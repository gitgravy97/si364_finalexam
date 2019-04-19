from django.urls import path, reverse_lazy
from . import views

urlpatterns = [
    path('', views.AdListView.as_view()),
    path('ads', views.AdListView.as_view(), name='ads'),
    path('ad/<int:pk>', views.AdDetailView.as_view(), name='ad_detail'),
    
    path('ad/create', views.AdFormView.as_view(success_url=reverse_lazy('ads')), name='ad_create'),
    path('ad/<int:pk>/update', views.AdFormView.as_view(success_url=reverse_lazy('ads')), name='ad_update'),
    
    path('ad/<int:pk>/delete', views.AdDeleteView.as_view(success_url=reverse_lazy('ads')), name='ad_delete'),

    path('ad/<int:pk>/comment',
        views.CommentCreateView.as_view(), name='comment_create'),
    path('comment/<int:pk>/delete',
        views.CommentDeleteView.as_view(success_url=reverse_lazy('forums')), name='comment_delete'),
]