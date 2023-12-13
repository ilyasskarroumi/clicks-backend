from datetime import timezone
import os
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from django.core.files import File


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        print(f"Creating user with email: {email}, password: {password}")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        role = extra_fields.get('role')
        if role:
            profile = os.path.join(settings.BASE_DIR, f'user_profiles/{role.lower().replace(" ", "_")}.png')
            with open(profile, 'rb') as photo_file:
                user.profile.save(f'{user.email}_{role.lower().replace(" ", "_")}.png', File(profile), save=False)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    ROLES = [
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('Client', 'Client'),
        ('Media Buyer', 'Media Buyer'),
        ('Page Builder', 'Page Builder'),
        ('Voice Over', 'Voice Over'),
        ('Video Editor', 'Video Editor')
    ]

    USER_STATUS = [
        ('Available', 'Available'),
        ('Busy', 'Busy'),
        ('Not Available', 'Not Available')
    ]
    
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=30, choices=ROLES)
    status = models.CharField(max_length=30, choices=USER_STATUS, blank=True, null=True)
    profile = models.FileField(upload_to='user_profiles/', blank=True, null=True)
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

class Client(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    user = models.OneToOneField(User, limit_choices_to={'role': 'Client'}, on_delete=models.CASCADE)
    commission = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def create_client(self, email, password, **extra_fields):
        # Set the role to 'Client' by default
        extra_fields.setdefault('role', 'Client')
        
        # Create a new user with the specified role
        user = User.objects.create_user(email=email, password=password, **extra_fields)

        # Create a new client instance
        client = self.objects.create(user=user, **extra_fields)
        
        return client
    
    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        if self.user:
            self.user.delete()
    
    def __str__(self):
        return self.user.email


class Product(models.Model):
    PRODUCT_TYPES = [
        ('Testing', 'Testing'),
        ('Scaling', 'Scaling'),
        ('Affiliate', 'Affiliate'),
    ]

    PRODUCT_STATUS = [
        ('New', 'New'),
        ('Not Approved', 'Not Approved'),
        ('Approved', 'Approved'),
        ('Awaiting Landing Page', 'Awaiting Landing Page'),
        ('Awaiting Creatives', 'Awaiting Creatives'),
        ('Published', 'Published'),
    ]

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(Client, blank=True, null=True, on_delete=models.SET_NULL, related_name="product_client")
    media_buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'Media Buyer'}, related_name="product_media_buyer")
    name = models.CharField(max_length=100, blank=True, null=True)
    image = models.FileField(upload_to='products/', default='products/product_default.png', blank=True, null=True)
    link = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=20, blank=True, null=True, choices=PRODUCT_TYPES)
    sourcing_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    service_provider = models.CharField(max_length=30, blank=True, null=True)
    country = models.CharField(max_length=30, blank=True, null=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    upsell_status = models.CharField(max_length=20, blank=True, null=True)
    upsell_offers = models.CharField(max_length=55, blank=True, null=True)
    AOV = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    test_cpp = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    decision = models.CharField(max_length=30, blank=True, null=True)
    status = models.CharField(max_length=30, blank=True, null=True, choices=PRODUCT_STATUS, default="New")

    def __str__(self):
        return self.name


class Campaign(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    client = models.ForeignKey(Client, blank=True, null=True, on_delete=models.SET_NULL, related_name="campaign_client")
    media_buyer = models.ForeignKey(User, blank=True, null=True, limit_choices_to={'role': 'Media Buyer'}, on_delete=models.SET_NULL, related_name="campaign_media_buyer")
    product = models.ForeignKey(Product, blank=True, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100, blank=True, null=True)
    started_date = models.DateField(blank=True, null=True)
    ended_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    platform = models.CharField(max_length=20, blank=True, null=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leads = models.IntegerField(blank=True, null=True)
    amount_spent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.name

    
class Payment(models.Model):
    PAYMENT_TYPES = [
        ('Membership', 'Membership'),
        ('Ads Balance', 'Ads Balance'),
        ('Leads Balance', 'Leads Balance'),
        ('Wrong Orders', 'Wrong Orders'),
    ]

    APPROVAL_STATUS = [
        ('Approved', 'Approved'),
        ('Waiting Approval', 'Waiting Approval'),
        ('Not Approved', 'Not Approved')
    ]

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    client = models.ForeignKey(Client, blank=True, null=True, on_delete=models.CASCADE, related_name="payment_client")
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    proof = models.FileField(upload_to='payment_proofs/', blank=True, null=True)
    type = models.CharField(max_length=20, choices=PAYMENT_TYPES, blank=True, null=True)
    status = models.CharField(max_length=20, choices=APPROVAL_STATUS, default="Waiting Approval", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.client.user.email


STATUS = [
    ('To Do', 'To Do'),
    ('In Progress', 'In Progress'),
    ('Done', 'Done'),
]

LANGUAGES = [
    ('Arabic', 'Arabic'),
    ('French', 'French'),
    ('English', 'English')
]

class Page(models.Model):
    TYPES = [
        ('Product Page', 'Product Page'),
        ('Landing Page', 'Landing Page')
    ]

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    media_buyer = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, limit_choices_to={'role': 'Media Buyer'}, related_name="page_media_buyer")
    creator = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, limit_choices_to={'role': 'Page Builder'},  related_name="page_creator")
    product = models.ForeignKey(Product, blank=True, null=True, on_delete=models.SET_NULL)
    type = models.CharField(max_length=30, blank=True, null=True, choices=TYPES)
    store = models.CharField(max_length=55, blank=True, null=True)
    language = models.CharField(max_length=20, blank=True, null=True, choices=LANGUAGES)
    status = models.CharField(max_length=20, blank=True, null=True, choices=STATUS, default="To Do")
    final_link = models.CharField(max_length=255, blank=True, null=True)
    note = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.product.name


class VoiceOver(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    media_buyer = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, limit_choices_to={'role': 'Media Buyer'}, related_name="voice_over_media_buyer")
    creator = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, limit_choices_to={'role': 'Voice Over'}, related_name="voice_over_creator")
    product = models.ForeignKey(Product, blank=True, null=True, on_delete=models.SET_NULL)
    language = models.CharField(max_length=20, blank=True, null=True, choices=LANGUAGES)
    script = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True, choices=STATUS, default="To Do")
    final_link = models.CharField(max_length=255, blank=True, null=True)
    note = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.product.name


class Creative(models.Model):
    FORMATS = [
        ('Reel (9:16)', 'Reel (9:16)'),
        ('Square (1:1)', 'Square (1:1)'),
        ('widescreen (16:19)', 'widescreen (16:19)'),
        ('Vertical (4:5)', 'Vertical (4:5)')
    ]

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    media_buyer = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, limit_choices_to={'role': 'Media Buyer'}, related_name="creative_media_buyer")
    creator = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, limit_choices_to={'role': 'Video Editor'}, related_name="creative_creator")
    product = models.ForeignKey(Product, blank=True, null=True, on_delete=models.SET_NULL)
    voice_over = models.ForeignKey(VoiceOver, blank=True, null=True, on_delete=models.SET_NULL, related_name="creative_voice_over")
    format = models.CharField(max_length=30, blank=True, null=True, choices=FORMATS)
    language = models.CharField(max_length=20, blank=True, null=True, choices=LANGUAGES)
    is_voice_over = models.BooleanField(blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True, choices=STATUS, default="To Do")
    final_link = models.CharField(max_length=255, blank=True, null=True)
    note = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.product.name