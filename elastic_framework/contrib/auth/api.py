
def get_base_field_user_model(user_model):
    '''Retrieve all base field of user model used by your app
    Args:
       user_model: instance of the user model, use get_user_model() from Django
       to get it
    Returns:
       username_fieldname
       password_fieldname
       status_field fieldname
       active_status_value
       facebook_user_id_fieldname UserId fieldname for facebokk authentiction
    '''
    assert user_model is not None
    return (getattr(user_model, 'USERNAME_FIELD', 'username'),
            getattr(user_model, 'PASSWORD_FIELD', 'password'),
            getattr(user_model, 'STATUS_FIELD', ''),
            getattr(user_model, 'ACTIVE_STATUS_VALUE', ''),
            getattr(user_model, 'FACEBOOK_USER_ID_FIELD', None)
            )
