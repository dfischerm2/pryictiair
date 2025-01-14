from django.urls import re_path

from landing.views.adm_callforpapers import callPaperView
from landing.views.adm_committee import committeeMemberView
from landing.views.adm_committee_category import committeeCategoryView
from landing.views.adm_guideline import guidelineView
from landing.views.adm_guideline_type import guidelineTypeView
from landing.views.adm_important_date import importantDateView
from landing.views.adm_principalcarrousel import carrouselImageView
from landing.views.adm_sponsor import sponsorView
from landing.views.adm_sponsor_category import sponsorCategoryView
from landing.views.adm_summary import summaryView
from landing.views.adm_summary_image import summaryImageView
from landing.views.adm_topic import topicView
from landing.views.adm_topic_categories import topicCategoryView
from landing.views.view_conference import conferenceView
from landing.views.view_notificacions import personNotificacionView
from landing.views.view_feesconference import conferenceFeesView

landing_urls = (
    {
        "nombre": "Sponsors Category",
        "url": 'sponsor_category/',
        "vista": sponsorCategoryView,
    },
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
        "nombre": "Summary Image",
        "url": 'summary/images/',
        "vista": summaryImageView,
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
        "nombre": "Carrousel",
        "url": 'carrousel/',
        "vista": carrouselImageView,
    },
    {
        "nombre": "Call For Papers",
        "url": 'call_paper/',
        "vista": callPaperView,
    },
    {
        "nombre": "Important dates",
        "url": 'important_date/',
        "vista": importantDateView,
    },
    {
        "nombre": "Notifications",
        "url": 'notified/',
        "vista": personNotificacionView,
    },
    {
        "nombre": "Conference",
        "url": 'conference/',
        "vista": conferenceView,
    },
    {
        "nombre": "Conference Fees",
        "url": 'conference_fees/',
        "vista": conferenceFeesView,
    },
)

urlpatterns = []

for u in landing_urls:
    urlpatterns.append(re_path(r'^{}$'.format(u["url"]), u["vista"]))
