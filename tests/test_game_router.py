from fastapi import status


def test_play_question(client_test):
    response = client_test.get('/questions/1')
    assert response.status_code == status.HTTP_200_OK


def test_play_questions_ok(client_user):
    response = client_user.get('/questions/1')
    assert response.status_code == status.HTTP_200_OK
