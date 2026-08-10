from django.urls import path

from .views import LSASearchView


urlpatterns = [
    path(
        "v1/lsas/search/",
        LSASearchView.as_view(),
        name="lsa-search",
    ),
]