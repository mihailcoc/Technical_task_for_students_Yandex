from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework import filters, mixins, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .models import Company, Position, Employee
from users.models import CustomUser
from .filter import EmployeeFilter
from .pagination import CustomPagination
from .permissions import (IsAdminOrReadOnly, IsAdminModeratorOwnerOrReadOnly,
                          IsAdmin)
from .serializers import PositionSerializer, CompanySerializer
from .serializers import UserSerializer, UserEditSerializer, RegisterSerializer
from .serializers import EmployeeWriteSerializer, EmployeeReadSerializer
from .serializers import TokenSerializer


User = get_user_model()


class PositionViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                      mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ('name')
    search_fields = ['name', ]
    lookup_field = 'slug'


class CompanyViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                     mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ('name')
    search_fields = ['name', ]
    lookup_field = 'slug'


class EmployeeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = EmployeeFilter

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return EmployeeWriteSerializer
        return EmployeeReadSerializer


class EmployeeEditViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeWriteSerializer
    permission_classes = (IsAdminModeratorOwnerOrReadOnly,)

    def get_company(self):
        company_id = self.kwargs.get('company_id')
        company = get_object_or_404(
            Company.objects.prefetch_related('employees'),
            id=company_id
        )
        return company

    def get_queryset(self):
        company = self.get_company()
        return company.employees.all()

    @action(
        methods=['post', ],
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
    )
    def perform_create(self, serializer):
        company = get_object_or_404(Company, pk=self.kwargs.get('company_id'))
        serializer.save(author=self.request.user, company=company)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EmployeePhoneEditViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeWriteSerializer
    permission_classes = (IsAdminModeratorOwnerOrReadOnly,)

    def get_queryset(self):
        employee = get_object_or_404(
            Employee, pk=self.kwargs.get('employee_id'))
        return employee.phones.all()

    @action(
        methods=['post', ],
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
    )
    def perform_create(self, serializer):
        employee = get_object_or_404(
            Employee, pk=self.kwargs.get('employee_id'),
            company_id=self.kwargs.get('company_id'))
        serializer.save(author=self.request.user, employee=employee)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = (IsAdmin,)

    @action(
        methods=['get', 'patch', ],
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=UserEditSerializer,
    )
    def me(self, request):
        user = request.user
        if request.method == "GET":
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == "PATCH":
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    user = get_object_or_404(
        CustomUser,
        username=serializer.validated_data['username'],
        email=serializer.validated_data['email']
    )
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject="YaMDb registration",
        message=f"Your confirmation code: {confirmation_code}",
        from_email=None,
        recipient_list=[user.email],
    )

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def get_jwt_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        CustomUser,
        username=serializer.validated_data["username"]
    )

    if default_token_generator.check_token(
        user, serializer.validated_data["confirmation_code"]
    ):
        token = AccessToken.for_user(user)
        return Response({"token": int(token)}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
