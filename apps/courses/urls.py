#!/usr/bin/python
#coding:utf-8
__author__ = 'zaxlct'
__date__ = '2017/4/7 上午9:58'

from django.conf.urls import url
from .views import CourseListView, CourseDetailView, CourseInfoView, CourseLessonView, CommentView, AddCommentView, VideoPlayView

urlpatterns = [
    # 课程列表页
    url(r'^list/$', CourseListView.as_view(), name='course_list'),
    # 课程详情页
    url(r'^detail/(?P<course_id>\d+)/$', CourseDetailView.as_view(), name='course_detail'),

    # 课程章节信息
    url(r'^info/(?P<course_id>\d+)/$', CourseInfoView.as_view(), name='course_info'),
    # 课程章节详情
    url(r'^lesson/(?P<lesson_id>\d+)/$', CourseLessonView.as_view(), name='course_lesson'),
    # 评论页面

    url(r'^comment/(?P<course_id>\d+)/$', CommentView.as_view(), name='course_comment'),
    # 添加课程评论
    url(r'^add_comment/$', AddCommentView.as_view(), name='add_comment'),

    # 播放视频
    url(r'^video/(?P<video_id>\d+)/$', VideoPlayView.as_view(), name='video_play'),
]
