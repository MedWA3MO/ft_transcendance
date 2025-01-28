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
import fnmatch

User = get_user_model()
logger = logging.getLogger(__name__)


User = get_user_model()

class TokenVerificationMiddleWare:
	def __init__(self, get_response):
		self.get_response = get_response
		self.logger = logging.getLogger(__name__)

	def __call__(self, request):
		# Log request details
		self.logger.info(f"Processing request path: {request.path}")
		self.logger.debug(f"Available cookies: {request.COOKIES}")
		self.logger.info(f"Headers: {request.headers}")
		self.logger.info(f"Method: {request.method}")

		# For profile data path, add extra logging
		if request.path == '/backend/profile/data':
			self.logger.info("=== Processing Profile Data Request ===")
			self.logger.info(f"Request Method: {request.method}")
			self.logger.info(f"Content Type: {request.content_type}")
			self.logger.info(f"Request Headers: {dict(request.headers)}")
			self.logger.info(f"Cookies Present: {list(request.COOKIES.keys())}")
			if request.method == 'POST':
				try:
					self.logger.info(f"Request Body: {request.body.decode('utf-8')}")
				except:
					self.logger.info("Could not decode request body")

		if request.method == 'OPTIONS':
			response = self.get_response(request)
			return response

		unrestricted_paths = [
			"/",
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
			'/backend/ws/',
			'/ws/',
			'/ws/global/',
			'/ws/four_game/',
			'/ws/online/',
			"/backend/notifications/unread",
			"/backend/profile/data",
			"/backend/searchItems/*",
		]
		request.customUser = AnonymousUser()

		# Check if path is unrestricted
		if request.path.startswith("/backend/admin") or any(fnmatch.fnmatch(request.path, pattern) for pattern in unrestricted_paths):
			self.logger.info(f"Unrestricted path: {request.path}")
			if request.path == '/backend/profile/data':
				self.logger.info("Profile data path accessed as unrestricted")
			return self.get_response(request)

		# Token verification
		refresh_token = request.COOKIES.get("jwt")
		access_token = request.COOKIES.get("jwt-access")

		if request.path == '/backend/profile/data':
			self.logger.info(f"Refresh token present: {bool(refresh_token)}")
			self.logger.info(f"Access token present: {bool(access_token)}")

		if not refresh_token:
			self.logger.warning("No refresh token found in request")
			return JsonResponse(
				{"error": "refresh token not found or invalid"},
				status=status.HTTP_401_UNAUTHORIZED,
			)

		try:
			refresh_token_obj = RefreshToken(refresh_token)
			self.logger.info("Successfully validated refresh token")
			request.unique_key = refresh_token_obj.payload.get("channel_name")

			if request.path == '/backend/profile/data':
				self.logger.info(f"Channel name from token: {request.unique_key}")

			if not access_token:
				self.logger.info("No access token found, generating new one")
				new_access_token = refresh_token_obj.access_token
				user_id = AccessToken(new_access_token).get("user_id")
				request.customUser = User.objects.get(id=user_id)

				if request.path == '/backend/profile/data':
					self.logger.info(f"Generated new access token for user ID: {user_id}")

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

				if request.path == '/backend/profile/data':
					self.logger.info(f"Using existing access token for user ID: {user_id}")

				return self.get_response(request)
			except (TokenError, User.DoesNotExist) as e:
				self.logger.warning(f"Token error or user not found: {str(e)}")
				new_access_token = refresh_token_obj.access_token
				user_id = AccessToken(new_access_token).get("user_id")
				request.customUser = User.objects.get(id=user_id)

				if request.path == '/backend/profile/data':
					self.logger.info(f"Generated replacement access token for user ID: {user_id}")

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

		except TokenError as e:
			self.logger.error(f"Token validation failed: {str(e)}")
			if request.path == '/backend/profile/data':
				self.logger.error(f"Profile data request failed due to token error: {str(e)}")
			response = JsonResponse(
				{"error": "refresh token invalid"},
				status=status.HTTP_401_UNAUTHORIZED
			)
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

class RequestLoggingMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response
		self.logger = logging.getLogger(__name__)

	def __call__(self, request):
		# Pre-processing
		self.logger.info(f"""
		Request details:
		Path: {request.path}
		Method: {request.method}
		Content-Type: {request.content_type}
		Headers: {dict(request.headers)}
		Body: {request.body.decode() if request.method == 'POST' else 'N/A'}
		""")

		try:
			response = self.get_response(request)
			
			# Post-processing
			self.logger.info(f"""
			Response details:
			Status code: {response.status_code}
			Content-Type: {response.get('Content-Type')}
			""")
			
			return response
		except Exception as e:
			self.logger.error(f"Error in middleware: {str(e)}")
			raise