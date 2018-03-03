#!/usr/bin/python
#coding:utf-8
import json

from django.shortcuts import render
from django.views.generic.base import View
from django.db.models import Q
from django.http import HttpResponse

from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from .models import Course, Lesson, CourseResource, Video
from operation.models import UserFavorite, UserCourse, UserLesson, CourseComments
from utils.mixin_utils import LoginRequiredMixin

from keras.models import load_model
import numpy as np
import gensim
import traceback
import os
# Create your views here.

print("load model")
# lstm-arols
model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),'courses/lstm_arols/')
window_size = 5
vector_size = 128
#cluster = request.user.ols_cluster
word2vec_model = gensim.models.Word2Vec.load(model_path+'w2vmodel_'+str(vector_size))
word_vectors = word2vec_model.wv
del word2vec_model
lstm_model = load_model(model_path+'model_0.h5')
lstm_model.predict(np.zeros((1, window_size, vector_size)))
print("model test done.")

# 课程列表首页
class CourseListView(View):
    def get(self, request):
        all_courses = Course.objects.all().order_by('-add_time')
        hot_courses = Course.objects.all().order_by('-click_nums')[:3]

        #课程搜索
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_courses = all_courses.filter(
                Q(name__icontains=search_keywords) |
                Q(desc__icontains=search_keywords) |
                Q(detail__icontains=search_keywords)
            )

        # 课程排序
        sort = request.GET.get('sort', '')
        if sort == 'students':
            all_courses = all_courses.order_by('-students')
        elif sort == 'hot':
            all_courses = all_courses.order_by('-click_nums')

        # 对课程进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_courses, 3, request=request)
        courses = p.page(page)

        return render(request, 'course-list.html', {
            'all_courses': courses,
            'hot_courses': hot_courses,
            'sort': sort,
        })


# 课程详情
class CourseDetailView(View):
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))

        # 课程点击数 + 1
        course.click_nums += 1
        course.save()

        # 找到相关课程
        tag = course.tag
        relate_courses = []
        if tag:
            relate_courses = Course.objects.filter(tag=tag)[:2]

        # 课程/机构收藏
        has_fav_course = False
        has_fav_org = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True

        return render(request, 'course-detail.html', {
            'course': course,
            'relate_courses': relate_courses,
            'has_fav_course': has_fav_course,
            'has_fav_org': has_fav_org,
        })


# 课程信息
class CourseInfoView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        course.students +=1
        course.save()

        # 查询用户是否已经学习了该课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            # 这里不用
            # user_courses.user = request.user
            # user_courses.course = course
            # 因为 user，course 是外键，在 UserCourse 实际上存储的是 id ，这些 id 是已经存在的
            user_courses = UserCourse(user=request.user, course=course)
            user_courses.save()

        # 得出学过该课程的同学还学过的课程
        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user.id for user_course in user_courses]
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        course_ids = [user_course.course.id for user_course in all_user_courses]

        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]

        all_resources = CourseResource.objects.filter(course=course)
        return render(request, 'course-video.html', {
            'course': course,
            'all_resources': all_resources,
            'relate_courses': relate_courses,
        })

# 章节信息
class CourseLessonView(LoginRequiredMixin, View):
    def get(self, request, lesson_id):
        lesson = Lesson.objects.get(id=int(lesson_id))
        course = lesson.course

        # 查询用户是否已经学习了该课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            # 这里不用
            # user_courses.user = request.user
            # user_courses.course = course
            # 因为 user，course 是外键，在 UserCourse 实际上存储的是 id ，这些 id 是已经存在的
            user_courses = UserCourse(user=request.user, course=course)
            user_courses.save()

        # 记录用户行为日志
        course_lesson = UserLesson()
        course_lesson.lesson = lesson
        course_lesson.user = request.user
        course_lesson.save()

        # lstm-arols
        #seq = ['882617','883092','882609','882617','882537']
        log_seq = UserLesson.objects.filter(user=request.user).order_by('-add_time')[:5]
        #print(log_seq)
        pred_lessons = list()
        
        try:
            tmp = list()
            for item in log_seq:
                item_id = str(item.lesson.arols_id)
                #print(item_id)
                if item_id in word_vectors.vocab:
                    tmp.append(word_vectors[item_id])
            tmp = np.asarray(tmp)
            if len(tmp)==window_size:
                pred_vec = lstm_model.predict(tmp.reshape(1, window_size, vector_size))
                pred_set = word_vectors.most_similar(positive=pred_vec, topn=5)
                for rmd_lesson in pred_set:
                    pred_lessons.append(rmd_lesson[0])
        except Exception as e:
            print(e)
        

        # 得出学过该课程的同学还学过的课程
        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user.id for user_course in user_courses]
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        course_ids = [user_course.course.id for user_course in all_user_courses]

        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]

        all_resources = CourseResource.objects.filter(course=course)
        return render(request, 'course-lesson.html', {
            'lesson': lesson,
            'course': course,
            'all_resources': all_resources,
            'relate_courses': relate_courses,
            'pred_lessons':pred_lessons,
        })


# 课程评论
class CommentView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        all_resources = CourseResource.objects.filter(course=course)
        all_comments = CourseComments.objects.filter(course=course)

        # 得出学过该课程的同学还学过的课程
        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user.id for user_course in user_courses]
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        course_ids = [user_course.course.id for user_course in all_user_courses]
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]

        return render(request, 'course-comment.html', {
            'course': course,
            'all_comments': all_comments,
            'all_resources': all_resources,
            'relate_courses': relate_courses,
        })


# 添加评论
class AddCommentView(View):
    def post(self, request):
        # 判断用户登录状态
        res = dict()
        if not request.user.is_authenticated():
            res['status'] = 'fail'
            res['msg'] = u'用户未登录'
            return HttpResponse(json.dumps(res), content_type='application/json')

        course_id = int(request.POST.get('course_id', 0))
        comments = request.POST.get('comments', '')

        if course_id and comments:
            course_comments = CourseComments()
            course_comments.course = Course.objects.get(id=course_id)
            course_comments.comments = comments
            course_comments.user = request.user
            course_comments.save()
            res['status'] = 'success'
            res['msg'] = u'添加成功'
        else:
            res['status'] = 'fail'
            res['msg'] = u'添加失败'

        return HttpResponse(json.dumps(res), content_type='application/json')


# 课程信息
class VideoPlayView(LoginRequiredMixin, View):
    def get(self, request, video_id):
        video = Video.objects.get(id=int(video_id))
        course = video.lesson.course

        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            user_courses = UserCourse(user=request.user, course=course)
            user_courses.save()

        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user.id for user_course in user_courses]
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        course_ids = [user_course.course.id for user_course in all_user_courses]

        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]

        all_resources = CourseResource.objects.filter(course=course)
        return render(request, 'course-play.html', {
            'course': course,
            'all_resources': all_resources,
            'relate_courses': relate_courses,
            'video': video,
        })