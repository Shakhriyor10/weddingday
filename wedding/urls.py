from django.urls import path

from wedding.views import HotAppetizersList, ArtistList, WeddingDetailView, delete_comment

urlpatterns = [
    path('<int:pk>/', WeddingDetailView.as_view(), name='home'),
    path('<int:pk>/comments/<int:comment_pk>/delete/', delete_comment, name='delete_comment'),
    path('kitchen/<int:pk>/', HotAppetizersList.as_view(), name='hot_appetizers'),
    path('singers/<int:pk>/', ArtistList.as_view(), name='singers')
]
