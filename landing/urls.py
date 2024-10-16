from django.urls import re_path

from landing.views.adm_committee import committeeMemberView
from landing.views.adm_committee_category import committeeCategoryView
from landing.views.adm_guideline import guidelineView
from landing.views.adm_guideline_type import guidelineTypeView
from landing.views.adm_sponsor import sponsorView
from landing.views.adm_summary import summaryView
from landing.views.adm_topic import topicView
from landing.views.adm_topic_categories import topicCategoryView
from landing.views.view_notificacions import personNotificacionView

landing_urls = (
    {
        "nombre": "Sponsors",
        "url": 'sponsor/',
        "vista": sponsorView,
    },
    {
        "nombre": "Topic categories",
        "url": 'topic_categories/',
        "vista": topicCategoryView,
    },
    {
        "nombre": "Topic",
        "url": 'topic/',
        "vista": topicView,
    },
    {
        "nombre": "Guideline type",
        "url": 'guideline_type/',
        "vista": guidelineTypeView,
    },
    {
        "nombre": "Guideline",
        "url": 'guideline/',
        "vista": guidelineView,
    },
    {
        "nombre": "Summary",
        "url": 'summary/',
        "vista": summaryView,
    },
    {
        "nombre": "Committee category",
        "url": 'committee_category/',
        "vista": committeeCategoryView,
    },
    {
        "nombre": "Committee member",
        "url": 'committee_member/',
        "vista": committeeMemberView,
    },
    {
        "nombre": "Notifications",
        "url": 'notified/',
        "vista": personNotificacionView,
    },
)

urlpatterns = []

for u in landing_urls:
    urlpatterns.append(re_path(r'^{}$'.format(u["url"]), u["vista"]))
