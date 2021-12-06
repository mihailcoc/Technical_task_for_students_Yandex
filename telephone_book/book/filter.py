from django_filters import rest_framework as rest

from .models import Employee


class EmployeeFilter(rest.FilterSet):
    name = rest.CharFilter(field_name='name', lookup_expr='contains')
    surname = rest.CharFilter(field_name='surname', lookup_expr='contains')
    patronymic = rest.CharFilter(field_name='patronymic', lookup_expr='contains')
    company = rest.CharFilter(
        field_name='company__slug',
        lookup_expr='contains'
    )
    work_phone_number = rest.CharFilter(
        field_name='work_phone_number__slug',
        lookup_expr='contains'
    )
    private_phone_number = rest.CharFilter(
        field_name='private_phone_number__slug',
        lookup_expr='contains'
    )

    class Meta:
        model = Employee
        fields = ['name', 'surname', 'patronymic',  'work_phone_number', 'private_phone_number', 'company']