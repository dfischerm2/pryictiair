from django.conf.urls import url
from django.urls import path

from .acerade import acercade
from .index import index
from .view_changepass import changepass

#from .view_pago import pagoView
from .view_registro import registro
from .view_restaurar import restaurar
from .view_login import login_tienda, logout_tienda
from .view_recordarusername import recordarusername
from .view_perfil import perfil


urlpatterns = [
    path('', index),
    url(r'^acercade/', acercade),
    #path('pago/<str:pedido_id>/', pagoView),
    url(r'^perfil/', perfil),
    # url(r'^register/', registro),
    url(r'^login/', login_tienda),
    url(r'^logout/', logout_tienda),
    url(r'^restorepass/', restaurar),
    url(r'^restoreusername/', recordarusername),
    url(r'^changepass/', changepass),

]
