from django.http import Http404
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from api.models import *
from api.serializers import *
from decimal import Decimal
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class UserClientPermission(BasePermission):
    allowed_roles = {'Admin'}

    def has_permission(self, request, view):
        return request.user and request.user.role in self.allowed_roles

class IsAdminManagerUser(BasePermission):
    allowed_roles = {'Admin', 'Manager'}

    def has_permission(self, request, view):
        return request.user and request.user.role in self.allowed_roles

class PaymentPermission(BasePermission):
    allowed_roles = {'Admin', 'Manager', 'Client'}

    def has_permission(self, request, view):
        return request.user and request.user.role in self.allowed_roles
    
class ProductPermission(BasePermission):
    allowed_roles = {'Admin', 'Manager', 'Client'}
    media_buyer_allowed_methods = {'GET', 'PUT'}

    def has_permission(self, request, view):
        if request.method in self.media_buyer_allowed_methods:
            self.allowed_roles.add('Media Buyer')
        else:
            self.allowed_roles.discard('Media Buyer')
        return request.user and request.user.role in self.allowed_roles
    
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['role'] = self.user.role
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserListView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, UserClientPermission)
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.exclude(Q(pk=self.request.user.pk) | Q(role="Client"))
    
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, UserClientPermission)
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.exclude(pk=self.request.user.pk)


# Create your views here.
# class UserView(APIView):
#     permission_classes = (IsAuthenticated, UserClientPermission)

#     def post(self, request):
#         # Create a new user
#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def get(self, request):
#         users = User.objects.exclude(Q(pk=request.user.pk) | Q(role="Client"))
#         serializer = UserSerializer(users, many=True)
#         return Response(serializer.data)

#     def put(self, request, pk):
#         # Edit a user
#         try:
#             user = User.objects.exclude(pk=request.user.pk).get(pk=pk)
#         except User.DoesNotExist:
#             raise Http404
#         serializer = UserSerializer(user, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         # Delete a user
#         try:
#             user = User.objects.exclude(pk=request.user.pk).get(pk=pk)
#         except User.DoesNotExist:
#             raise Http404
#         user.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
    

class BaseUserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]  # Common permission for all subclasses

    def get_queryset(self):
        return User.objects.filter(role=self.user_role)

class MediaBuyerListView(BaseUserListView):
    user_role = 'Media Buyer'
    permission_classes = [PaymentPermission]

class PageBuilderListView(BaseUserListView):
    user_role = 'Page Builder'
    permission_classes = [PaymentPermission]
    

class ClientListView(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = (IsAuthenticated, UserClientPermission)

    def create(self, request):
        user_data = {
            'first_name': request.data.get('user[first_name]', ''),
            'last_name': request.data.get('user[last_name]', ''),
            'status': request.data.get('user[status]', ''),
            'role': 'Client',
            'email': request.data.get('user[email]', ''),
            'password': request.data.get('user[password]', '')
        }
        existing_user = User.objects.filter(email=user_data['email']).first()
        if existing_user:
            raise serializers.ValidationError({'user': {'email': 'User with this email already exists for another user.'}})
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user_instance = user_serializer.save()
            commission_data = request.data.get('commission', '')
            commission = Decimal(commission_data) if commission_data else 0
            client = Client.objects.create(user=user_instance, commission=commission)
            return Response(ClientSerializer(client).data, status=status.HTTP_201_CREATED)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = (IsAuthenticated, UserClientPermission)

    def update(self, request, pk):
        client = Client.objects.filter(pk=pk).first()
        if client:
            user_data = {
                'first_name': request.data.get('user[first_name]', ''),
                'last_name': request.data.get('user[last_name]', ''),
                'status': request.data.get('user[status]', ''),
                'role': 'Client',
                'email': request.data.get('user[email]', ''),
                'password': request.data.get('user[password]', '')
            }
            existing_user = User.objects.exclude(pk=client.user.pk).filter(email=user_data['email']).first()
            if existing_user:
                raise serializers.ValidationError({'user': {'email': 'User with this email already exists for another user.'}})
            user_serializer = UserSerializer(client.user, data=user_data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()
            commission_data = request.data.get('commission', '')
            client.commission = Decimal(commission_data) if commission_data else 0
            client.save()
            return Response(ClientSerializer(client).data, status=status.HTTP_200_OK)
        return Response({'error': 'Client not found!'}, status=status.HTTP_404_NOT_FOUND)
    

# class ClientView(APIView):
#     permission_classes = (IsAuthenticated, UserClientPermission)

#     def post(self, request):
#         request.data['user']['role'] = 'Client'
#         print(request.data)
#         serializer = ClientSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def get(self, request):
#         clients = Client.objects.all()
#         serializer = ClientSerializer(clients, many=True)
#         return Response(serializer.data)

#     def put(self, request, pk):
#         try:
#             client = Client.objects.get(pk=pk)
#         except Client.DoesNotExist:
#             raise Http404
#         # Update User data
#         user_serializer = UserSerializer(client.user, data=request.data.get('user'), partial=True)
#         if user_serializer.is_valid():
#             user_serializer.save()

#             # Update Client data
#             client_serializer = ClientSerializer(client, data=request.data, partial=True)
#             if client_serializer.is_valid():
#                 client_serializer.save()
#                 return Response(client_serializer.data)
#             return Response(client_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         try:
#             client = Client.objects.get(pk=pk)
#         except Client.DoesNotExist:
#             raise Http404
#         client.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
    

class PaymentListView(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated, PaymentPermission)

    def get_queryset(self):
        user = self.request.user
        if user.role in ["Admin", "Manager"]:
            return Payment.objects.all()
        elif user.role == "Client":
            return Payment.objects.filter(client=user.client)
        return Payment.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role in ["Admin", "Manager"]:
            client = Client.objects.get(pk=self.request.data.get('client', ''))
        elif user.role == "Client":
            client = user.client
            serializer.validated_data['status'] = "Waiting Approval"
        serializer.save(client=client)

class PaymentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated, PaymentPermission)

    def perform_update(self, serializer):
        user = self.request.user
        if user.role == "Admin" or user.role == "Manager" :
            client = Client.objects.get(pk=self.request.data.get('client', ''))
            serializer.save(client=client)
        elif user.role == "Client":
            serializer.validated_data['status'] = "Waiting Approval"
            serializer.save()


# media_buyer_data = request.data.get('media_buyer', '')
# media_buyer = User.objects.filter(pk=media_buyer_data).first() if media_buyer_data else None
# media_buyer_data = request.data.get('media_buyer', '')
# media_buyer_id = media_buyer_data.id if hasattr(media_buyer_data, 'id') else media_buyer_data
# client.media_buyer = User.objects.filter(pk=media_buyer_id).first() if media_buyer_data else None


class ProductListView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated, ProductPermission)

    def get_queryset(self):
        user = self.request.user
        if user.role in ["Admin", "Manager"]:
            return Product.objects.all()
        elif user.role == "Client":
            return Product.objects.filter(client=user.client)
        elif user.role == "Media Buyer":
            return Product.objects.filter(media_buyer=user)
        return Product.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.role == "Client":
            serializer.validated_data['client'] = user.client
        media_buyer = self.request.data.get('media_buyer', '')
        media_buyer_id = self.request.data.get('media_buyer', '')
        media_buyer = get_object_or_404(User, pk=media_buyer_id) if media_buyer_id else None
        serializer.validated_data['media_buyer'] = media_buyer
        serializer.save()

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated, ProductPermission)

    def perform_update(self, serializer):
        user = self.request.user
        if user.role in ["Admin", "Manager", "Client"]:
            if user.role == "Client":
                serializer.validated_data['client'] = user.client
            media_buyer_id = self.request.data.get('media_buyer', '')
            media_buyer = get_object_or_404(User, pk=media_buyer_id) if media_buyer_id else None
            serializer.validated_data['media_buyer'] = media_buyer
        else:
            serializer.validated_data.pop('client', None)
            serializer.validated_data.pop('media_buyer', None)
        serializer.save()


class CampaignListView(generics.ListCreateAPIView):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = (IsAuthenticated,)

class CampaignDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = (IsAuthenticated,)


class PageListView(generics.ListCreateAPIView):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = (IsAuthenticated,)
    
    def perform_create(self, serializer):
        serializer.save(media_buyer=self.request.user)

class PageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = (IsAuthenticated,)


class VoiceOverListView(generics.ListCreateAPIView):
    queryset = VoiceOver.objects.all()
    serializer_class = VoiceOverSerializer
    permission_classes = (IsAuthenticated,)
    
    def perform_create(self, serializer):
        serializer.save(media_buyer=self.request.user)

class VoiceOverDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = VoiceOver.objects.all()
    serializer_class = VoiceOverSerializer
    permission_classes = (IsAuthenticated,)


class CreativeListView(generics.ListCreateAPIView):
    queryset = Creative.objects.all()
    serializer_class = CreativeSerializer
    permission_classes = (IsAuthenticated,)
    
    def perform_create(self, serializer):
        serializer.save(media_buyer=self.request.user)

class CreativeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Creative.objects.all()
    serializer_class = CreativeSerializer
    permission_classes = (IsAuthenticated,)


# class PageView(APIView):
#     permission_classes = (IsAuthenticated)

#     def post(self, request):
#         serializer = PageSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def get(self, request):
#         pages = Page.objects.filter(pk=request.user.pk)
#         serializer = PageSerializer(pages, many=True)
#         return Response(serializer.data)

#     def put(self, request, pk):
#         try:
#             page = Page.objects.get(pk=pk)
#         except Page.DoesNotExist:
#             raise Http404
#         serializer = PageSerializer(page, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         try:
#             page = Page.objects.get(pk=pk)
#         except Page.DoesNotExist:
#             raise Http404
#         page.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)