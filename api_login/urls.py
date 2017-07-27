from django.conf.urls import url
from api_login.views import (
		LoginView,
		RegistrationView,
		ForgotPasswordView,
		ActivationUserView,
		UserDetailsView,
		UpdateUserDetailsView,
		CQGRegistrationView,
		FailedOnBoardingView,
		ResetPasswordView,
		UserProfileView,
		UserUpdateView,
		ChangePasswordView,
		UpdateProfilePicView,
		RemoveProfilePicView
	)

from strategies.views import (
		TradersSubSectorView,
		TradersContractsView,
		TradersSpreadsView
	)

# import django.views.static

urlpatterns = [
	url(r'^login/$', LoginView.as_view()),
	url(r'^registration/$', RegistrationView.as_view()),
	url(r'^cqg/registration/$', CQGRegistrationView.as_view()),
	url(r'^forgotpassword/$', ForgotPasswordView.as_view()),
	url(r'^resetpassword/$', ResetPasswordView.as_view()),
	url(r'^activation/(?P<user_id>[0-9]+)/$', ActivationUserView.as_view()),
	url(r'^user/details/$', UserDetailsView.as_view()),
	url(r'^update/user/details/$', UpdateUserDetailsView.as_view()),
	url(r'^failed/onboarding/$', FailedOnBoardingView.as_view()),
	url(r'^traders/subsector/$', TradersSubSectorView.as_view()),
	url(r'^traders/contracts/$', TradersContractsView.as_view()),
	url(r'^traders/spreads/$', TradersSpreadsView.as_view()),
	url(r'^user/profile/$', UserProfileView.as_view()),
	url(r'^user/profile/update/(?P<user_id>[0-9]+)/$', UserUpdateView.as_view()),
	url(r'^user/change/password/(?P<user_id>[0-9]+)/$', ChangePasswordView.as_view()),
	url(r'^user/profile/pic/update/(?P<user_id>[0-9]+)/$', UpdateProfilePicView.as_view()),
	url(r'^user/profile/pic/remove/(?P<user_id>[0-9]+)/$', RemoveProfilePicView.as_view()),
]