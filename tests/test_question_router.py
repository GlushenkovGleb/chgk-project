from fastapi import status


def test_get_home(client_test):
    response = client_test.get('/home')
    assert response.status_code == status.HTTP_200_OK


def test_get_create_ok(client_test):
    response = client_test.get('/questions/create')
    assert response.status_code == status.HTTP_200_OK


def test_get_create_user(client_user):
    response = client_user.get('/questions/create')
    assert response.status_code == status.HTTP_200_OK


def test_create_question(client_user):
    question_data = {
        'title': 'title',
        'desc': 'description',
        'cost': '100',
        'answer': 'user',
    }
    response = client_user.post('/questions/create', data=question_data)
    assert response.status_code == status.HTTP_200_OK


def test_questions_written_ok(client_user):
    response = client_user.get('/questions/written')
    assert response.status_code == status.HTTP_200_OK

    response = client_user.get('/questions/played')
    assert response.status_code == status.HTTP_200_OK


def test_questions_written_no_user(client_test):
    response = client_test.get('/questions/written')
    assert response.status_code == status.HTTP_200_OK

    response = client_test.get('/questions/played')
    assert response.status_code == status.HTTP_200_OK
