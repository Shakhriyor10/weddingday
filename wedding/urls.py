from django.urls import path

from wedding.views import HotAppetizersList, ArtistList, WeddingDetailView

urlpatterns = [
    path('<int:pk>/', WeddingDetailView.as_view(), name='home'),
    path('kitchen/<int:pk>/', HotAppetizersList.as_view(), name='hot_appetizers'),
    path('singers/<int:pk>/', ArtistList.as_view(), name='singers')
]
