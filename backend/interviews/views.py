from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.response import Response
from .models import InterviewSession
from .services import evaluate_answer, generate_question

def _api_error(error):
    message = str(error)
    lowered = message.lower()
    if "429" in lowered or "quota" in lowered or "rate" in lowered:
        detail = "Помощник получил слишком много запросов. Подождите минуту и попробуйте снова."
    else:
        detail = "Не удалось связаться с помощником. Мы уже повторили запрос — попробуйте ещё раз через минуту."
    return Response({"detail": detail}, status=status.HTTP_502_BAD_GATEWAY)

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
def create_question(request):
    role = str(request.data.get("role", "")).strip()
    description = str(request.data.get("vacancy_description", "")).strip()
    mode = str(request.data.get("mode", "technical")).strip()
    if not role:
        return Response({"detail": "Укажите роль или направление."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        data = generate_question(role, description, mode)
        if not data["question"]:
            raise ValueError("Gemini вернул пустой вопрос.")
        user = request.user if request.user.is_authenticated else None
        session = InterviewSession.objects.create(user=user, role=role, mode=mode, vacancy_description=description, question=data["question"])
        return Response({"id": session.id, **data}, status=status.HTTP_201_CREATED)
    except Exception as error:
        return _api_error(error)

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
def submit_answer(request, session_id):
    answer = str(request.data.get("answer", "")).strip()
    if len(answer) < 10:
        return Response({"detail": "Ответ должен содержать не менее 10 символов."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        session = InterviewSession.objects.get(pk=session_id)
    except InterviewSession.DoesNotExist:
        return Response({"detail": "Сессия не найдена."}, status=status.HTTP_404_NOT_FOUND)
    try:
        if session.user and session.user != request.user:
            return Response({"detail": "Эта сессия принадлежит другому пользователю."}, status=status.HTTP_403_FORBIDDEN)
        feedback = evaluate_answer(session.role, session.question, answer, session.mode)
        session.answer, session.score, session.feedback = answer, feedback["score"], feedback
        session.save(update_fields=["answer", "score", "feedback"])
        return Response(feedback)
    except Exception as error:
        return _api_error(error)

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def history(request):
    rows = InterviewSession.objects.filter(user=request.user).exclude(answer="")[:50]
    return Response([{"id": x.id, "role": x.role, "mode": x.mode, "question": x.question, "score": x.score, "created_at": x.created_at} for x in rows])

@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    username = str(request.data.get("username", "")).strip()
    password = str(request.data.get("password", ""))
    if len(username) < 3 or len(password) < 6:
        return Response({"detail": "Имя — минимум 3 символа, пароль — минимум 6."}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(username__iexact=username).exists():
        return Response({"detail": "Такое имя уже занято."}, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.create_user(username=username, password=password)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "username": user.username}, status=status.HTTP_201_CREATED)

@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    user = authenticate(username=str(request.data.get("username", "")), password=str(request.data.get("password", "")))
    if not user:
        return Response({"detail": "Неверное имя или пароль."}, status=status.HTTP_400_BAD_REQUEST)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "username": user.username})
