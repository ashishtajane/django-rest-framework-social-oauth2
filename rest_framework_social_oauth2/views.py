# -*- coding: utf-8 -*-

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

from oauth2_provider.models import Application, AccessToken, RefreshToken
from oauth2_provider.ext.rest_framework import OAuth2Authentication
from oauthlib.common import generate_token
from .authentication import SocialAuthentication
from .settings import PROPRIETARY_APPLICATION_NAME

from django.utils import timezone
from datetime import timedelta


@api_view(['GET'])
@authentication_classes([SocialAuthentication])
@permission_classes([permissions.IsAuthenticated])
def convert_token(request):
    try:
        app = Application.objects.get(name=PROPRIETARY_APPLICATION_NAME)
    except Application.DoesNotExist:
        return Response({
            "detail": "The server's oauth2 application is not setup or misconfigured"
        }, status=status.HTTP_501_NOT_IMPLEMENTED)

    token = AccessToken.objects.create(user=request.user, application=app,
        token=generate_token(), expires=timezone.now() + timedelta(days=1),
        scope="read write")
    refresh_token = RefreshToken.objects.create(access_token=token,
        token=generate_token(), user=request.user, application=app)
    code = status.HTTP_201_CREATED

    return Response({
        "access_token": token.token,
        "refresh_token": refresh_token.token,
        "token_type": "Bearer",
        "expires_in": int((token.expires - timezone.now()).total_seconds()),
        "scope": token.scope
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@authentication_classes([OAuth2Authentication])
@permission_classes([permissions.IsAuthenticated])
def invalidate_sessions(request):
    try:
        app = Application.objects.get(name=PROPRIETARY_APPLICATION_NAME)
    except Application.DoesNotExist:
        return Response({
            "detail": "The server's oauth2 application is not setup or misconfigured"
        }, status=status.HTTP_501_NOT_IMPLEMENTED)

    tokens = AccessToken.objects.filter(user=request.user, application=app)
    tokens.delete()
    return Response({}, status=status.HTTP_204_NO_CONTENT)
