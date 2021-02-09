from flask import Blueprint, abort
from flask_restful import (Resource, Api, reqparse, inputs, fields,
                           marshal, marshal_with, url_for)

import models

course_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'url': fields.String,
    'reviews': fields.List(fields.String)
}


def add_reviews(course):
    course.reviews = [url_for('resources.reviews.review', id=review.id)
                      for review in course.review_set]


def course_or_404(course_id):
    try:
        course = models.Course.get(models.Course.id == course_id)
    except models.Course.DoesNotExist:
        abort(404, description='Course {} does not exist.'.format(course_id))
    else:
        return course


class CourseList(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'title',
            required=True,
            help='No course title provided.',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'url',
            type=inputs.url,
            required=True,
            help='No course URL provided.',
            location=['form', 'json']
        )
        super().__init__()

    def get(self):
        courses = [marshal(add_reviews(course), course_fields)
                   for course in models.Course.select()]
        """marshal serializes course."""
        return {'courses': courses}

    def post(self):
        args = self.reqparse.parse_args()
        course = models.Course.create(**args)
        return (add_reviews(course), 201, {
                'Location': url_for('resources.courses.course', id=course.id)})


class Course(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'title',
            required=True,
            help='No course title provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'url',
            required=True,
            help='No course URL provided',
            location=['form', 'json'],
            type=inputs.url
        )
        super().__init__()

    @marshal_with(course_fields)
    def get(self, id):
        """Returns single record. Marshaled to course_fields format"""
        return add_reviews(course_or_404(id))

    @marshal_with(course_fields)
    def put(self, id):
        """Returns tuple. Updated record, status 200, headers dict"""
        args = self.reqparse.parse_args()
        query = models.Course.update(**args).where(models.Course.id == id)
        query.execute()
        return (add_reviews((models.Course.get(models.Course.id == id))),
                200,
                {'Location': url_for('resources.courses.course', id=id)})

    def delete(self, id):
        """Returns tuple. Empty body, empty body status code, headers"""
        query = models.Course.delete().where(models.Course.id == id)
        query.execute()
        return ('',
                204,
                {'Location': url_for('resources.courses.course')})


courses_api = Blueprint('resources.courses', __name__)
api = Api(courses_api)
api.add_resource(
    CourseList,
    '/courses',
    endpoint='courses'
)
api.add_resource(
    Course,
    '/courses/<int:id>',
    endpoint='course'
)
