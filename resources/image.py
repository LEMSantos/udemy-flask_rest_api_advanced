from flask_restful import Resource
from flask_uploads import UploadNotAllowed
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from libs import image_helper
from libs.strings import gettext
from schemas.image import ImageSchema

image_schema = ImageSchema()


class ImageUpload(Resource):
    @jwt_required()
    def post(self):
        """Used to upload an image file. It uses JWT to retrive user
        information and then saves the image to the user's folder. If there
        is a file name conflict, it appends a number at the end.
        """
        data = image_schema.load(request.files)
        user_id = get_jwt_identity()
        folder = f'user_{user_id}'

        try:
            image_path = image_helper.save_image(data['image'], folder=folder)
            basename = image_helper.get_basename(image_path)

            return {
                'message': gettext('image_uploaded').format(basename=basename)
            }, 201
        except UploadNotAllowed:
            extension = image_helper.get_extension(data['image'])

            return {
                'message': gettext('image_illegal_extension').format(
                    extension=extension,
                )
            }, 400
