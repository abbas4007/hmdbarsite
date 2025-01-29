from django.contrib.auth import views
from django.urls import path
from .views import (
    ArticleList,
    ArticleCreate,
    ArticleUpdate,
    ArticleDelete,
    AddVakil,
    vakileList,
    Riyasatlist,
vakil_image_view,
VakilUpdate,
ComisionList,
AddComision,
AazaComision,
ComisionDetail,

)

app_name = 'account'

urlpatterns = [
	path('', ArticleList.as_view(), name="home"),
	path('vakillist', vakileList.as_view(), name="vakil_list"),
	path('comisionlist', ComisionList.as_view(), name="comision_list"),
	# path('azacomisionlist/<str:name>', AazaComision.as_view(), name="aza_list"),
    path('vakil/update/<int:id>', VakilUpdate.as_view(), name="vakil_update"),
    path('comisiondetail/<int:id>', ComisionDetail.as_view(), name="comision_detail"),
	path('riyasatlist', Riyasatlist.as_view(), name="riyasat_list"),
	path('addvakil', AddVakil.as_view(), name="vakil_add"),
	path('addcomision', AddComision.as_view(), name="comision_add"),
    path('article/create', ArticleCreate.as_view(), name="article_create"),
    path('article/update/<int:pk>', ArticleUpdate.as_view(), name="article_update"),
	path('article/delete/<int:pk>', ArticleDelete.as_view(), name="article_delete"),

    path('image_upload/<int:id>', vakil_image_view.as_view(), name = 'image_upload'),

]