from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from datetime import datetime

from classic_tetris_project.facades.user_permissions import UserPermissions
from classic_tetris_project.util import lazy
from ..forms.live_notification import LiveNotificationForm
from .base import BaseView

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('data/firebase_credentials.json')
app = firebase_admin.initialize_app(cred)
db = firestore.client()

class LiveNotificationsView(PermissionRequiredMixin, BaseView):
    permission_required = UserPermissions.SEND_LIVE_NOTIFICATIONS

class LiveView(LiveNotificationsView):
    def get(self, request):
        return render(request, "live_notifications/live.haml")


class SubmitView(LiveNotificationsView):
    def get(self, request):
        return render(request, "live_notifications/submit.haml", {
            "live_notification_form": LiveNotificationForm(),
        })

    def post(self, request):
        live_notification_form = LiveNotificationForm(request.POST)
        if live_notification_form.is_valid():
            doc_ref = db.collection(u'notifications').document(u'current')
            doc_ref.set({
                u'message': live_notification_form.cleaned_data.get("message"),
                u'duration': live_notification_form.cleaned_data.get("duration"),
                u'position': live_notification_form.cleaned_data.get("position"),
                u'created_at': datetime.now()
            })
            messages.info(self.request, "Message Submitted")

        return render(request, "live_notifications/submit.haml", {
            "live_notification_form": LiveNotificationForm(),
        })
