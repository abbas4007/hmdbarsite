from django.urls import path
from .views import (
	ArticleList,
	ArticleDetail,
	ArticlePreview,
	CategoryList,
	VokalaView,
	VakilCity,
	VakilPage,
	ArticleSearchList,
	UploadExcelView

)
app_name = "home"
urlpatterns = [
	path('upload-excel/', UploadExcelView.as_view(), name = 'upload_excel'),
	path('', ArticleList.as_view(), name="home"),
	# path('page/<int:page>/', ArticleList.as_view(), name="home"),
	path('article/<slug:slug>/', ArticleDetail.as_view(), name="detail"),
	path('vokala/', VokalaView.as_view(), name="vokala"),
	path('city/<str:city>/', VakilCity.as_view(), name="vokala_city"),
	path('preview/<int:pk>/', ArticlePreview.as_view(), name="preview"),
	path('vakil/<int:id>/', VakilPage.as_view(), name="vakil"),
	path('category/<slug:slug>/', CategoryList.as_view(), name="category"),
	path('category/<slug:slug>/page/<int:page>/', CategoryList.as_view(), name="category"),
	path('search/', ArticleSearchList.as_view(), name = 'search_articles'),

]