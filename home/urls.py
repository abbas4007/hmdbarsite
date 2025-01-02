from django.urls import path
from .views import (
	ArticleList,
	ArticleDetail,
	ArticlePreview,
	CategoryList,
	SearchList,
    VokalaView,
    VakilCity,
	VakilPage,
	ComisionView,
	ComisionDetailView,
	Contact,
)

app_name = "home"
urlpatterns = [
	path('', ArticleList.as_view(), name="home"),
	path('page/<int:page>', ArticleList.as_view(), name="home"),
	path('article/<slug:slug>', ArticleDetail.as_view(), name="detail"),
	path('vokala/', VokalaView.as_view(), name="vokala"),
	path('city/<slug:city>', VakilCity.as_view(), name="vokala_city"),
	path('comision/', ComisionView.as_view(), name="comision"),
	# path('riyasat/', RiyastView.as_view(), name="riyasat"),
	path('preview/<int:pk>', ArticlePreview.as_view(), name="preview"),
	path('vakil/<int:id>', VakilPage.as_view(), name="vakil"),
	path('category/<slug:slug>', CategoryList.as_view(), name="category"),
	path('category/<slug:slug>/page/<int:page>', CategoryList.as_view(), name="category"),
	path('search/', SearchList.as_view(), name="search"),
	path('search/page/<int:page>', SearchList.as_view(), name="search"),
	path('contact', Contact.as_view(), name="contact"),
	# path('admin/home/vakil/update_image/UpdateImageView', UpdateImageView.as_view(), name='vakil_update_image'),
]