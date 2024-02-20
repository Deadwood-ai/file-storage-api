from supabase import create_client


from .settings import settings


def login(user: str, password: str):
    # create a supabase client
    client = create_client(settings.supabase_url, settings.supabase_key)

    auth_response = client.auth.sign_in_with_password({'email': user, 'password': password})
    
    client.auth.sign_out()
    # return the response
    return auth_response


def verify_token(jwt: str) -> str:
    # create a supabase client
    client = create_client(settings.supabase_url, settings.supabase_key)

    # try to retrieve the user by the given JWT
    response = client.auth.get_user(jwt=jwt)

    client.auth.sign_out()
    # up to now, we only extract the user id from the response
    # TODO: we could do more here
    return response.user.id

    