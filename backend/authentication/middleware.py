from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.tokens import TokenError
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from channels.exceptions import DenyConnection
from django.http import JsonResponse
from rest_framework import status
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class TokenVerificationMiddleWare:
	def __init__(self, get_response):
		self.get_response = get_response
		self.logger = logging.getLogger(__name__)

	def __call__(self, request):
		if request.method == 'OPTIONS':
			response = self.get_response(request)
			return response

		self.logger.info(f"Processing request path: {request.path}")
		self.logger.debug(f"Available cookies: {request.COOKIES}")
		self.logger.info(f"Headers: {request.headers}")

		unrestricted_paths = [
			"/backend/auth/login/42", 
			"/backend/auth/callback/42",
			"/backend/signup", 
			"/backend/login", 
			"/backend/logout",
			"/backend/token", 
			"/backend/token/refresh",
			"/backend/reset-password",
			"/backend/forgot-password",
			'/backend/2fa/verify/user/', 
			'/backend/2fa/verify/user',
			'/backend/ws/',  # Add WebSocket paths
			'/ws/',  # Add WebSocket paths
			'/ws/global/',
			'/ws/four_game/',
			'/ws/online/',
			"/backend/notifications/unread",
		]
		request.customUser = AnonymousUser()

		if request.path.startswith("/backend/admin") or request.path in unrestricted_paths:
			self.logger.info(f"Unrestricted path: {request.path}")
			return self.get_response(request)

		refresh_token = request.COOKIES.get("jwt")
		access_token = request.COOKIES.get("jwt-access")

		if not refresh_token:
			return JsonResponse(
				{"error": "refresh token not found or invalid"},
				status=status.HTTP_401_UNAUTHORIZED,
			)

		try:
			refresh_token_obj = RefreshToken(refresh_token)
			self.logger.info("Successfully validated refresh token")
			request.unique_key = refresh_token_obj.payload.get("channel_name")

			if not access_token:
				new_access_token = refresh_token_obj.access_token
				user_id = AccessToken(new_access_token).get("user_id")
				request.customUser = User.objects.get(id=user_id)

				response = self.get_response(request)
				response.set_cookie(
					key="jwt-access",
					value=str(new_access_token),
					httponly=True,
					samesite="Lax",
					secure=True,
					max_age=api_settings.ACCESS_TOKEN_LIFETIME.total_seconds(),
				)
				return response

			try:
				user_id = AccessToken(access_token).get("user_id")
				request.customUser = User.objects.get(id=user_id)
				return self.get_response(request)
			except (TokenError, User.DoesNotExist):
				new_access_token = refresh_token_obj.access_token
				user_id = AccessToken(new_access_token).get("user_id")
				request.customUser = User.objects.get(id=user_id)

				response = self.get_response(request)
				response.set_cookie(
					key="jwt-access",
					value=str(new_access_token),
					httponly=True,
					samesite="Lax",
					secure=True,
					max_age=api_settings.ACCESS_TOKEN_LIFETIME.total_seconds(),
				)
				return response
		except TokenError:
			response = JsonResponse({"error": "refresh token invalid"}, status=status.HTTP_401_UNAUTHORIZED)
			self.logger.error(f"Token validation failed: {str(TokenError)}")
			response.delete_cookie("jwt")
			response.delete_cookie("jwt-access")
			return response

		return self.get_response(request)

class UserOnlineStatusMiddleware(BaseMiddleware):
	async def __call__(self, scope, receive, send):
		try:
			headers = dict(scope["headers"])
			access_token = None

			if b'cookie' in headers:
				cookie_str = headers[b'cookie'].decode('utf-8')
				cookies_dict = dict(cookie.split('=', 1) for cookie in cookie_str.split('; '))
				access_token = cookies_dict.get('jwt-access')

			if not access_token:
				scope['user'] = AnonymousUser()
			try:
				user = await self.get_user_from_token(str(access_token))
				scope['user'] = user
			except TokenError:
				scope['user'] = AnonymousUser()

			if isinstance(scope['user'], AnonymousUser):
				raise DenyConnection("Authentication Required!")
		except Exception as e:
			logger.error(f"\nConnection Denied: {e}\n")
		return await super().__call__(scope, receive, send)

	@database_sync_to_async
	def get_user_from_token(self, token):
		try:
			user_id = AccessToken(token).get("user_id")
			user = User.objects.get(id=user_id)
			return user
		except (TokenError, User.DoesNotExist):
			raise TokenError("token is not valid")