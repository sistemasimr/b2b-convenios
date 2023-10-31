# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from ...models import User
from django.contrib.auth import get_user_model
User = get_user_model()

class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, User):
        token = super(LoginSerializer, cls).get_token(User)
        return token


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ['id', 'document']