
from django.urls import path, re_path

from .acerade import acercade
from .index import index, index_copy
from .view_changepass import changepass

#from .view_pago import pagoView
from .view_registro import registerView
from .view_restaurar import restaurar
from .view_login import login_tienda, logout_tienda
from .view_recordarusername import recordarusername
from .view_perfil import perfil


urlpatterns = [
    path('', index_copy),
    re_path(r'^test_landing/', index_copy),
    re_path(r'^acercade/', acercade),
    #path('pago/<str:pedido_id>/', pagoView),
    re_path(r'^perfil/', perfil),
    # url(r'^register/', registro),
    re_path(r'^login/', login_tienda),
    re_path(r'^logout/', logout_tienda),
    re_path(r'^restorepass/', restaurar),
    re_path(r'^restoreusername/', recordarusername),
    re_path(r'^changepass/', changepass),
    re_path(r'^register/', registerView),

]
