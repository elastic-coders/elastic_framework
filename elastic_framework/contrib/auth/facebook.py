import requests
from django.conf import settings

# this two url at the moment is not used
DEBUG_TOKEN_URL = ('https://graph.facebook.com/debug_token?input_token={}'
                   '&access_token={}')
ACCESS_TOKEN_URL = ('https://graph.facebook.com/oauth/access_token?client_id={}'
                    '&client_secret={}&grant_type=client_credentials')
PROFILE_URL = 'https://graph.facebook.com/user/{}'

# We use this url to verify user authentication
VERIFY_URL = 'https://graph.facebook.com/v2.2/me?access_token={}'


def facebook_authentication(auth_data):
    ''' Verify accessToken passed in request data with facebook API
    to validate signup with facebook
    Verification is made asking for user profile using access token contained
    in auth_data

    Args:
      auth_data: a dictionary containing facebookAccessToken to be verified
         and facebook UserID to check if it is equl to facebook user id

    Returns:
      a dictionary containing user id that could be save into user model
    '''
    if not 'accessToken' in auth_data or not 'userId' in auth_data:
        return None, u'Insufficent data in auth request'
    req = requests.get(
        VERIFY_URL.format(auth_data['accessToken'])
    )
    facebook_data = req.json()
    if len(facebook_data) == 0:
        return None, u'No data retrieved from facebook'
    if not 'id' in facebook_data:
        return None, u'Authentication failed'
    user_id = facebook_data['id']
    if user_id != auth_data['userId']:
        return None, u'Wrong user id'
    return facebook_data, None

