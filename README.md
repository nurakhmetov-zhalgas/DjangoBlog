Учебный проект представляет собой собственный блог с системой подписок и коментариев, проект покрыт тестами.

Стек технологий:
Python3
Django
Pytest
Pillow
Bootstrap

Установка:
Выполнить pip install -r requirements.txt
Выполнить python3 manage.py runserver

# Финальное задание [Реализовано]

Осталось добавить в проект систему подписки на авторов и создать ленту их постов.

Задача вам знакома: создайте модель, напишите view-функцию, добавьте в `urls.py` новые пути, подготовьте шаблоны.

Клонируйте репозиторий **hw05_final** и скопируйте в него код из репозитория **hw04_tests**, в котором вы работали в этом спринте.

Можно приступать к заданию.

Модель **Follow** должна иметь такие поля:

- **user** — ссылка на объект пользователя, который подписывается. Укажите имя связи: `related_name="follower"`
- **author** — ссылка на объект пользователя, на которого подписываются, имя связи пусть будет `related_name="following"`

Напишите view-функцию страницы, куда будут выведены посты авторов, на которых подписан текущий пользователь.

Ещё две view-функции нужны для подписки на интересного автора и для того, чтобы отписаться от надоевшего графомана:

```PYTHON

@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    # ...
    return render(request, "follow.html", {...})

@login_required
def profile_follow(request, username):
    # ...
    pass

@login_required
def profile_unfollow(request, username):
    # ...
    pass` 




```

Добавьте необходимые адреса в `posts/urls.py`:

```PYTHON

urlpatterns = [
    # ...
    path("follow/", views.follow_index, name="follow_index"),
    path("<str:username>/follow/", views.profile_follow, name="profile_follow"), 
    path("<str:username>/unfollow/", views.profile_unfollow, name="profile_unfollow"),
] 
```

Теперь шаблоны.

Создайте шаблон `follow.html`, куда будут выводиться посты авторов, на которых подписан текущий пользователь. За образец можете взять шаблон `index.html`, только замените заголовок.

Добавьте в шаблоны `index.html` и `follow.html` виджет переключения лент `menu.html`:

```HTML

{% if user.is_authenticated %} 
<div class="row">
    <ul class="nav nav-tabs">
        <li class="nav-item">
            <a class="nav-link {% if index %}active{% endif %}" href="{% url 'index' %}">
                  Все авторы
            </a>
        </li>
        <li class="nav-item">
            <a class="nav-link {% if follow %}active{% endif %}" href="/follow">
                Избранные авторы
            </a>
        </li>
    </ul>
</div>
{% endif %}
```

Код `index.html`:

```HTML

{% extends "base.html" %} 
{% block title %} Последние обновления {% endblock %}

{% block content %}
<div class="container">

    {% include "menu.html" with index=True %}

        <h1>Последние обновления на сайте</h1>

        {% for post in page %}
            {% include "post_item.html" with post=post %}
        {% endfor %}

        {% if page.has_other_pages %}
            {% include "paginator.html" with items=page paginator=paginator %}
        {% endif %}

    </div>
{% endblock %}

```

На странице профайла добавьте ссылку «Подписаться» в левое меню:

```HTML
<li class="list-group-item">
    {% if following %}
    <a class="btn btn-lg btn-light" 
            href="{% url 'profile_unfollow' profile.username %}" role="button"> 
            Отписаться 
    </a> 
    {% else %}
    <a class="btn btn-lg btn-primary" 
            href="{% url 'profile_follow' profile.username %}" role="button">
    Подписаться 
    </a>
    {% endif %}
</li>
```

## Тестирование

Напишите тесты, проверяющие работу нового сервиса:

- Авторизованный пользователь может подписываться на других пользователей и удалять их из подписок.
- Новая запись пользователя появляется в ленте тех, кто на него подписан и не появляется в ленте тех, кто не подписан на него.
- Только авторизированный пользователь может комментировать посты.
