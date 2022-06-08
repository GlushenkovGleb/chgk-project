# homework8

### Техническое задание:

#### Платное ЧГК
Разработать сайт с платными вопросам, т.е. каждый пользователь может создать свой вопрос и выставить цену за него.
Другой пользователь может взять этот вопрос из общей базы. Если он решает этот вопрос, то у ему начисляется выигрыш,
а у автора вопроса деньги снимаются. И соответственно наоборот: если вопрос не решен, то у пользователя снимаются деньги,
а автор их получает. После отыгровки вопроса, вопрос больше играться не может никем. Должна присутсвовать авторизация, каждому пользователю при регистрации выдается 1000 у.е.

Создание вопроса должно включать:
1. Тема вопроса
2. Текст вопроса
3. Правильный ответ
4. Цена вопроса

Ограничения на вопросы:
1. При создании вопроса пользователем надо убедиться, что у него достаточно денег, что оплатить в случае неуспеха и снять их пока вопрос не отыгран.
2. Перед тем как пользователь играет вопрос, надо убедиться, что у него достаточно денег на оплату.
3. На отыгровку вопроса дается минута, если пользователь присылает вопрос позже, то ответ не принимается.
4. Если вопрос играется каким-то пользователем, то он уже не должен быть доступен для остальных пользователей.
5. Один пользователь не может одновременно играть несколько вопросов.

Должно быть доступно пользователю:
1. Количество денег на счету
2. История отыгранных вопросов
3. Главная страница с доступными вопросами
4. Страница со своими вопросами
5. История транзакций
6. Форма для создания вопроса

Усложненный вариант(не успею):
1. Реализовать модерация, т.е. если пользователь не согласны с ответом на вопрос, то на вопрос можно отправить жалобу,
которая будет передана модератору. Создать модерацию через админку.
2. Реализовать пагинацию и фильтрацию там, где есть списки.
3. Пользователь может отменить свой вопрос, если он не отыгран или не играется.

### Description:
Несложное веб приложение, в котором пользователь может зарегистрироваться и залогиниться,
получить вначале 1000 у.е. и начать писать и играть вопросы. Можно посмотреть написанные тобой вопросы и узнать их статус,
а также посмотреть историю отыгранных собой вопросов.

Пользователь может выбрать понравившийся title вопроса и начать его играть. Он перейдет на страницу вопроса,
увидит содержание вопроса и начнется обратный отсчет. Если время истекло, то игроку засчитывается поражение.

### Design:
Для реализации был выбран FastApi, но лучше бы использовался Flask.

Для того, чтобы узнать когда закончится время на вопрос был использован Redis и его expired events. 
Я не придумал как его(слушателя на expired events) красиво встроить в FastApi, поэтому у меня есть небезопасный эндпойт,
который запускает слушателя на background task. Также из-за это нельзя "красиво" завершить работу сервера(


### Run app:
    make up

### Create venv:
    make venv

### Run tests:
    make test

### Run linters:
    make lint

### Run formatters:
    make format

