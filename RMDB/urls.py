"""RMDB URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include,re_path
from R6K.views import account,home,filter,comment,share,download,show
from IXIA import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('r6k/login',account.login),
    path('logout',account.logout),
    path('r6k/register',account.register),
    path('user-info/changepwd',account.changepwd),
    path('user-info/resetpwd',account.resetpwd),
    path('user-info',account.userdetail),
    path('upload',home.upload),
    path('r6k/nodes',home.nodes_info),
    path('r6k/add-node',home.add_node),
    path('r6k/edit-node',home.edit_node),
    re_path('r6k/(?P<classify>((high)|(middle)|(lower)|(lowest)|(low)|(unused)|(unreachable)))',filter.classify),
    re_path('ixia/(?P<classify>((high)|(middle)|(lower)|(lowest)|(low)|(unused)))',filter.ixiaClassify),
    re_path('^api/', include("R6K.api_url")),
    path('r6k/get-comments',comment.get),
    re_path('r6k/add-comment/(?P<nid>\d+)',comment.add),
    re_path('r6k/comment/(?P<nid>\d+)',comment.show),
    path('r6k/add-ixia',views.add_ixia),
    path('r6k/edit-chassis',views.edit_chassis),
    path('r6k/dele-chassis',views.delete_chassis),
    path('r6k/edit-card',views.edit_card),
    path('r6k/dele-card',views.delete_card),
    path('r6k/edit-ports',views.edit_ports),
    path('r6k/del-ixia-port',views.del_ports),
    path('r6k/ixia',views.ixia),
    path('r6k',home.index),
    path('share/r6k',share.share_nodes),
    path('share/ixia',share.share_ixia),
    path('share/others',share.share_others),
    path('BulidData/', download.BulidData),
    re_path('show/(?P<type>((totalNodesOfTeam)|(totalNodesOfTestbed)|(lowUTENodesOfTeam)|(unusedNodesOfTeam)|(unreachableNodesOfTeam)|(lowUTEOfMonth)|(lowUTEOfTeam)|(lowUTEOfTestbed)|(lowUTEOfInterval)))', show.getData),
    re_path('download/(\w+)', download.download),
    re_path('^',home.pageNotFound),
]
