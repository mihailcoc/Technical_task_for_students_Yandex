ЗАПУСК.
Добрый день, для запуска приложения необходимо выполнить серию команд.

pip install --upgrade pip
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt

Далее необходимо установить приложения, который не устанавливаются через requirements или устанавливаются через него очень криво.
Это приложение позволяет экспортировать данные из стороннего файла в базу данных приложения через, администратора.

pip install django-import-export
pip install django-filter

Это приложение позволяет отображать телефонные номера в международном формате далее в ссылке подробно написано. https://www.delftstack.com/ru/howto/django/django-phone-number-field/

pip install django-phonenumber-field[phonenumbers]


Далее переходим в папку приложения
cd telephone_book

И проводим миграции.

python manage.py migrate

Запускаем сервер.
python manage.py runserver



ОПИСАНИЕ.
В программе Postman.

1 запрос. Отправляем OPTIONS запрос на адрес
http://127.0.0.1:8000/book/v1/auth/signup/

 для получения токена
{
    "username": "admin",
    "email": "admin@admin.ru"
}
И получаем ответ 200 Ok. Файл response1.


2 запрос. Отправляем POST запрос на адрес
http://127.0.0.1:8000/book/v1/auth/signup/

 для получения токена

{
    "username": "rozamundpike",
    "email": "rozamundpike@yandex.ru"
}

И получаем ответ 500 Internal server error.
Подробности в файле response2.
Токен получен и сохранён в кеше см строку 107 COOKIES. 

3 запрос. Снова отправляем тот же самый запрос.
И получаем ответ 400 bad request.
The request can not be fulfilled due to the bad syntax.
{"username":["This field must be unique."],"email":["This field must be unique."]}
Подробности в файле response3.

4 запрос. Отправляем POST запрос на адрес
http://127.0.0.1:8000/book/v1/companies/1/
{
    "name": "romashka"
}
И получаем ответ 401 Unauthorized.
Подробности в файле response4.
Все ответы сохранены в папке postman_reply.

Из всех этих запросов сделал вывод что пользователь "username": "rozamundpike", "email": "rozamundpike@yandex.ru" создан.
Токен получен и сохранён в кеше.
Создать компанию нельзя, потому что нужно предоставить в запросе данные пользователя.


5 запрос. Отправляем POST запрос на адрес
http://127.0.0.1:8000/book/v1/auth/token/
{
    "username": "rozamundpike",
    "email": "rozamundpike@yandex.ru"
}

На эти запросы получаем ответ 400 Bad request.
{"confirmation_code":["This field is required."]}
Подробности в файле response5.

На эти запросы получаем ответ 401 Unauthorized.
http://127.0.0.1:8000/book/v1/users/
http://127.0.0.1:8000/book/v1/users/me/

Вывод, сервис работает.



РЕАЛИЗАЦИЯ.
Реализовано задание со звёдочкой*
Поиск данных представлен по полям поиска название компании и наименование должности с помощью DjangoFilterBackend.
Также представлен поиск по частичному совпадению в поле name  название компании или наименование должности с помощью filters.SearchFilter.
Реализован поиск даннх по ФИО сотрудника, названию компании и номеру рабочего или личного телефона с помощью EmployeeFilter.

В сериалайзере EmployeeWriteSerializer  реализовано  условие, что у сотрудника должен быть хотя бы один телефон.

Создать организацию с одинаковым названием нельзя в сериализаторе CompanySerializer.

Поле телефонного номера реализовано с помощью сторонней библиотеки phonenumber_field.modelfields, и валидатора RegexValidator.
Поле личного телефона сотрудника реализовано с помощью models.OneToOneField.

Аутентификация в приложении реализована через email и пароль и токен.

Пользователь сайта и сотрудник фирмы — это две разные сущности и между собой не связаны.
Пользователь сайта реализован с помощью модели User и UserAdmin.
Сотрудник фириы реализован с помощью модели Employee.


В модели Employee а также в файле urls.py реализована иерархия:

    ООО Ромашка
        Иванов Сергей Петрович (Инженер)
            Факс: +74951234567
        Басурман Иван Павлович (Бухгалтер)
            Рабочий: +79161234567
            Факс: +74951234567
    ООО Василек
        Цветкова Яна Ивановна (Программист)
            Личный: +79161234567
            Факс: +74951234567
    ООО Гремучая ива
    И так далее

Для доступа к странице конкретной фирмы или сотрудника, необходимо так же выводить их id.
Например: router_v1.register(r'companies/(?P<company_id>\d+)/employees', EmployeeEditViewSet, basename='employeereview')

Для вывода списка организаций, элементов поиска и сотрудников организации, используется пагинатор CustomPagination.

При запросе конкретной организации выводится список всех сотрудников

Не авторизованный пользователь может только просматривать информацию с помощью разрешения IsAdminOrReadOnly.

Обычный авторизованный пользователь может с помощью разрешения IsAdminOrReadOnly:

    Создавать организации CompanyViewSet
    Просмотреть список организаций, в которых он может изменять данные сотрудников EmployeeViewSet.
    Добавлять и удалять сотрудников, редактировать их ФИО, должности и номера телефонов EmployeeEditViewSet.

Создатель организации имеет дополнительные права с помощью разрешения IsAdminModeratorOwnerOrReadOnly:

    Предоставить по email доступ любому пользователю к редактированию организации.
    Просмотреть список пользователей, которым доступно редактирование созданых им организаций.
    Отозвать права на редактирование.
    Изменять информацию об организации: адрес, название и описание.

Интерфейс суперпользователя (Django Admin).

    Суперпользователь может менять права пользователей в помощью полей:
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions',

Разработка

    Создайте пустой репозиторий и работайте в нем, когда будете готовы — запуште изменения и пришлите ссылку на репозиторий.
    Выделите наиболее важные задачи в этом проекте и делайте в зависимости от приоритета. Лучше сделать половину задач и будет цельное рабочее приложение, чем много мелких, но основная задача выполняться не будет.
    Разрабатывать приложение необходимо на Django REST Framework.
    Надо описать README.md файл с инструкцией по запуску.
    Ключевые моменты: архитектура приложения и качество кода.
    Приветствуются любые дополнения к данному ТЗ: весь дополнительный функционал необходимо описать в README.md
    Допускаются небольшие отсупления от ТЗ

