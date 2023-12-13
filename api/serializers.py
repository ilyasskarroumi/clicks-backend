from datetime import date
from rest_framework import serializers
from django.db.models import Sum
from api.models import *
from django.core.files import File
from django.conf import settings

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(allow_blank=True, write_only=True)

    class Meta:
        model = User
        fields = ['id', 'date_joined', 'first_name', 'last_name', 'email', 'role', 'status', 'profile', 'password']

    def create(self, validated_data):
        if 'password' not in validated_data or validated_data['password'] is None or validated_data['password'] == '':
            raise serializers.ValidationError({'password': 'This field may not be blank.'})
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # Hash the password
        role = validated_data.get('role')
        if role:
            profile = os.path.join(settings.BASE_DIR, f'media/user_profiles/{role.lower().replace(" ", "_")}.png')
            print(profile)
            with open(profile, 'rb') as photo_file:
                user.profile.save(f'{user.email}_{role.lower().replace(" ", "_")}.png', File(photo_file), save=False)
        user.save()
        return user

    def update(self, instance, validated_data):
        # Handle password update
        print(validated_data)
        if 'password' in validated_data:
            password = validated_data.pop('password')
            if password is not None and password != "":
                instance.set_password(password)  # Hash the new password
        if 'role' in validated_data:
            role = validated_data['role']
            if instance.role != role:
                profile = os.path.join(settings.BASE_DIR, f'media/user_profiles/{role.lower().replace(" ", "_")}.png')
                print(profile)
                with open(profile, 'rb') as photo_file:
                    instance.profile.save(f'{instance.email}_{role.lower().replace(" ", "_")}.png', File(photo_file), save=False)

        # Update other fields using the base class's update method
        return super(UserSerializer, self).update(instance, validated_data)


class ClientSerializer(serializers.ModelSerializer):
    ads_balance = serializers.SerializerMethodField()
    leads_balance = serializers.SerializerMethodField()
    membership = serializers.SerializerMethodField()
    user = UserSerializer(required=True)

    class Meta:
        model = Client
        fields = '__all__'
        depth = 1

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user_instance = user_serializer.save()
            client = Client.objects.create(user=user_instance, **validated_data)
            return client
        else:
            raise serializers.ValidationError({'user': user_serializer.errors})
    
    def update(self, instance, validated_data):
        # Update the user data if it exists in the request data
        user_data = validated_data.get('user')
        print(user_data)
        if user_data:
            user_instance = instance.user
            user_email = user_data.get('email')

            # Check if the provided email already exists for a different user
            existing_user = User.objects.exclude(id=user_instance.id).filter(email=user_email).first()
            if existing_user:
                raise serializers.ValidationError({'user': {'email': 'User with this email already exists for another user.'}})

            user_serializer = UserSerializer(user_instance, data=user_data, partial=True)

            if user_serializer.is_valid():
                user_serializer.save()

        # Update the Client instance
        return super(ClientSerializer, self).update(instance, validated_data)

    def get_ads_balance(self, client):
        # Calculate total payments with type 'Ads Balance'
        total_ads_payments = Payment.objects.filter(
            client=client,
            status="Approved",
            type='Ads Balance'
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Calculate total spent in all campaigns
        total_campaign_spent = Campaign.objects.filter(
            client=client,
        ).aggregate(total=Sum('amount_spent'))['total'] or 0

        return total_ads_payments - total_campaign_spent

    def get_leads_balance(self, client):
        # Calculate total payments with type 'Leads Balance'
        total_leads_payments = Payment.objects.filter(
            client=client,
            status="Approved",
            type='Leads Balance'
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_wrong_leads = Payment.objects.filter(
            client=client,
            status="Approved",
            type='Wrong Orders'
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Calculate total leads in all campaigns
        total_campaign_leads = Campaign.objects.filter(
            client=client,
        ).aggregate(total=Sum('leads'))['total'] or 0

        return total_leads_payments + total_wrong_leads - total_campaign_leads * client.commission

    def get_membership(self, client):
        # Check if there is a payment with type 'Membership' for the current month
        current_month_membership_payment = Payment.objects.filter(
            client=client,
            status="Approved",
            type='Membership',
            created_at__year=date.today().year,
            created_at__month=date.today().month
        ).exists()

        return current_month_membership_payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        depth = 2

class ProductSerializer(serializers.ModelSerializer):
    media_buyer = UserSerializer(read_only=True)
    client_name = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Product
        fields = '__all__'

    def get_client_name(self, obj):
        client = obj.client
        if client:
            return f"{client.user.first_name} {client.user.last_name}"
        return None

class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'

class PageSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = Page
        fields = '__all__'

class VoiceOverSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = VoiceOver
        fields = '__all__'

class CreativeSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = Creative
        fields = '__all__'