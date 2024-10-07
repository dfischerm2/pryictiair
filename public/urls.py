
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
    path(r'^acercade/', acercade),
    #path('pago/<str:pedido_id>/', pagoView),
    path(r'^perfil/', perfil),
    # url(r'^register/', registro),
    path(r'^login/', login_tienda),
    path(r'^logout/', logout_tienda),
    path(r'^restorepass/', restaurar),
    path(r'^restoreusername/', recordarusername),
    path(r'^changepass/', changepass),

]
