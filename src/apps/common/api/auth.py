from ninja import Router, Schema, ModelSchema
from ninja.security import django_auth
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.middleware.csrf import get_token

_User = get_user_model()


class LoginRequest(Schema):
    username: str
    password: str


class LoginSuccess(ModelSchema):
    class Config:
        model = _User
        model_fields = ["id", "username", "email", "first_name", "last_name"]


class LoginFailed(Schema):
    details: str = "Wrong username or password."


class CsrfToken(Schema):
    token: str


router = Router()


@router.get("/csrf-token")
def csrf_handshake(request):
    token = get_token(request)
    return {"csrf_token": token}


@router.get("/session", response={200: None, 403: None})
def check_session(request):
    if request.user.is_authenticated:
        return 200, None
    else:
        return 403, None


@router.post("/login", response={200: LoginSuccess, 401: LoginFailed})
def login_endpoint(request, credentials: LoginRequest):
    user = authenticate(
        request, username=credentials.username, password=credentials.password
    )
    if user:
        login(request, user)
        return 200, user
    else:
        return 401, {}


@router.get(
    "/profile",
    response={200: LoginSuccess, 401: LoginFailed},
    auth=django_auth,
)
def get_profile(request):
    return request.user


@router.post("/logout", response={204: None})
def logout_endpoint(request):
    logout(request)
    return 204, None


@router.get("/create-demo-users", response={204: None, 201: None})
def create_demo_users(request):
    for username, email, first_name, last_name, password in [
        ("fariz.tumbuan", "fariz.tumbuan@gmail.com", "Fariz", "Tumbuan", "P@ssw0rd"),
        ("user1", "user1@gmail.com", "User", "One", "P@ssw0rd"),
        ("user2", "user2@gmail.com", "User", "Two", "P@ssw0rd"),
        ("user3", "user3@gmail.com", "User", "Three", "P@ssw0rd"),
    ]:
        user, created = _User.objects.get_or_create(
            username=username,
            defaults={"email": email, "first_name": first_name, "last_name": last_name},
        )
        user.set_password(password)
        user.save()
    if created:
        return 201, None
    else:
        return 204, None
