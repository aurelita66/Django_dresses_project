from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('designers/', views.get_designers, name='designers-all'),
    path('designers/<int:designer_id>', views.get_one_designer, name='designer-one'),
    path('dresses/', views.DressListView.as_view(), name='dresses-all'),
    path('dresses/<int:pk>', views.DressDetailView.as_view(), name='dress-one'),
    path('search/', views.search, name='search'),
    path('mydresses/', views.RentedDressesByUserListView.as_view(), name='my-dresses'),
    path('register/', views.register_user, name='register'),
    path('profile/', views.get_user_profile, name='user-profile'),
    path('mydresses/new', views.DressRentalByUserCreateView.as_view(), name='my-rented-new'),
    path('mydresses/update/<int:pk>', views.DressRentalByUserUpdateView.as_view(), name='my-rented-update'),
    path('dresses/reviews/<int:pk>', views.DressReviewDeleteView.as_view(), name='reviews-delete'),
    path('allrents/', views.AllRentsView.as_view(), name='allrents'),
    path('rent/delete/<int:pk>/', views.DressRentalDeleteView.as_view(), name='delete-rent'),
    path('rent/update/<int:pk>/', views.DressRentalUpdateView.as_view(), name='update-rent'),

]
