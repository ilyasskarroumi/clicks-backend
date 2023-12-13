from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from .views import *

urlpatterns = [
    path('token', CustomTokenObtainPairView.as_view(), name ='token_obtain_pair'),
    path('token/refresh', jwt_views.TokenRefreshView.as_view(), name ='token_refresh'),
    path('users', UserListView.as_view(), name ='user-list'),
    path('user/<uuid:pk>', UserDetailView.as_view(), name ='user-detail'),
    path('media-buyers', MediaBuyerListView.as_view(), name='media-buyer-list'),
    path('page-builders', PageBuilderListView.as_view(), name='page-builder-list'),
    path('clients', ClientListView.as_view(), name='client-list'),
    path('client/<uuid:pk>', ClientDetailView.as_view(), name='client-detail'),
    path('payments', PaymentListView.as_view(), name='payment-list'),
    path('payment/<uuid:pk>', PaymentDetailView.as_view(), name='payment-detail'),
    path('products', ProductListView.as_view(), name='product-list'),
    path('product/<uuid:pk>', ProductDetailView.as_view(), name='product-detail'),
    path('campaigns', CampaignListView.as_view(), name='campaign-list'),
    path('campaign/<uuid:pk>', CampaignDetailView.as_view(), name='campaign-detail'),
    path('pages', PageListView.as_view(), name='page-list'),
    path('page/<uuid:pk>', PageDetailView.as_view(), name='page-detail'),
    path('voice-overs', VoiceOverListView.as_view(), name='voice-over-list'),
    path('voice-over/<uuid:pk>', VoiceOverDetailView.as_view(), name='voice-over-detail'),
    path('creatives', CreativeListView.as_view(), name='creative-list'),
    path('creative/<uuid:pk>', CreativeDetailView.as_view(), name='creative-detail')
]
