from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CompanyViewSet, EmployeeViewSet, PositionViewSet

from .views import EmployeeEditViewSet, EmployeePhoneEditViewSet, UserViewSet
from .views import register, get_jwt_token


router_v1 = DefaultRouter()
router_v1.register('companies', CompanyViewSet, basename='company')
router_v1.register('positions', PositionViewSet, basename='position')
router_v1.register('employees', EmployeeViewSet, basename='employee')
router_v1.register(
    r'companies/(?P<company_id>\d+)/employees', EmployeeEditViewSet,
    basename='employeereview')
router_v1.register(
    r'companies/(?P<company_id>\d+)/employees/(?P<employee_id>\d+)/phones',
    EmployeePhoneEditViewSet, basename='phone')
router_v1.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/signup/', register, name='register'),
    path('v1/auth/token/', get_jwt_token, name='token')
]
