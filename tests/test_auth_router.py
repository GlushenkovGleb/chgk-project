from fastapi import status


def test_show_register(client_test):
    response = client_test.get('/auth/register')
    assert response.status_code == status.HTTP_200_OK


def test_register_user(client_test):
    response = client_test.post(
        '/auth/register', data={'name': 'user4', 'password': 'user4'}
    )
    assert response.status_code == status.HTTP_302_FOUND


def test_register_exists(client_test):
    response = client_test.post(
        '/auth/register', data={'name': 'user3', 'password': 'user4'}
    )
    assert response.status_code == status.HTTP_200_OK


def test_show_login_user(client_test):
    response = client_test.get('/auth/login')
    assert response.status_code == status.HTTP_200_OK


def test_login_user_ok(client_test):
    response = client_test.post(
        '/auth/login', data={'name': 'user3', 'password': 'user3'}
    )
    assert response.status_code == status.HTTP_302_FOUND

    response = client_test.get('/auth/logout')
    assert response.status_code == status.HTTP_200_OK


def test_login_user_error(client_test):
    response = client_test.post(
        '/auth/login', data={'name': 'user3', 'password': 'user4'}
    )
    assert response.status_code == status.HTTP_200_OK
