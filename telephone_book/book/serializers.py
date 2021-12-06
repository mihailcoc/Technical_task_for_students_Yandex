from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth import get_user_model

from .models import Company, Position, Employee
from users.models import CustomUser


User = get_user_model()


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        exclude = ('id',)


class CompanySerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=Company.objects.all())])

    class Meta:
        model = Company
        exclude = ('id', )


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        exclude = ('id',)


class CategoryField(serializers.SlugRelatedField):
    def to_representation(self, value):
        return CompanySerializer(value).data


class PositionField(serializers.SlugRelatedField):
    def to_representation(self, value):
        return PositionSerializer(value).data


class EmployeeField(serializers.SlugRelatedField):
    def to_representation(self, value):
        return EmployeeSerializer(value).data


class EmployeeReadSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    position = PositionSerializer(read_only=True)
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = '__all__'


class EmployeeWriteSerializer(EmployeeReadSerializer):
    company = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Company.objects.all(),
    )
    position = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Position.objects.all(),
        many=True,
    )
    employee = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Employee.objects.all(),
    )

    class Meta:
        model = Employee
        fields = '__all__'
        validators = [UniqueTogetherValidator(
            queryset=Employee.objects.all(),
            fields=['work_phone_number', 'private_phone_number']
        )
        ]


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())])

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all())])

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'role', )
        model = CustomUser


class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = CustomUser
        read_only_fields = ('role',)


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())])

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())])

    class Meta:
        fields = ('username', 'email')
        model = CustomUser
        validators = [UniqueTogetherValidator(
            queryset=CustomUser.objects.all(),
            fields=['username', 'email']
        )
        ]

    def create(self, validated_data):
        user, created = CustomUser.objects.get_or_create(
            username=validated_data['username'],
            email=validated_data['email'],
            defaults={
                'username': validated_data['username'],
                'email': validated_data['email']})
        return user


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()