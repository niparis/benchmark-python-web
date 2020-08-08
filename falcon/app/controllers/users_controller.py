import logging
import datetime as dt

import falcon
import sqlalchemy
import attr

from app.models.users_models import User
from app.lib.validation import  ValidatedEntity, ValidateRequest

logger = logging.getLogger(__name__)


@attr.s(auto_attribs=True)
class UserCreation(ValidatedEntity):    
    full_name: str = attr.ib()
    email: str = attr.ib()  # should map to a segmentation column in databse
    password: str
    created_date: dt.datetime = None    
    is_active: bool = None
    is_superuser: bool = False
    user_id: int = None

    @property
    def json_response(self):
        return self.as_dict

    @classmethod
    def from_dict(cls, req, **kwargs) -> "UserCreation":
        return UserCreation(**kwargs)

class UsersManager:

    @falcon.before(ValidateRequest(UserCreation))
    def on_post(self, req, resp, user_creation: UserCreation, **kwargs):
        """POST /users/
            params: formid

            Returns: Questions for the requested questionnaire
        """      
        try:  
            user = User.create(**user_creation.as_dict_not_null)
        except sqlalchemy.exc.IntegrityError:
            raise falcon.HTTPError(
                falcon.HTTP_400,
                "User cannot be created, already exists",
            )
            
        # import ipdb; ipdb.set_trace()
        resp.media = user.as_dict

    
    def on_get(self, req, resp):
        """GET /users/{userid}/
            params: formid

            Returns: Questions for the requested questionnaire
        """
        user_id = req.get_param("user_id", required=True)
        user = User.get_one(user_id)    
        resp.media = user.json_response

    @falcon.before(ValidateRequest(UserCreation))
    def on_put(self, req, resp, user_creation, **kwargs):
        """PUT /users/{userid}/
            params: formid

            Returns: Questions for the requested questionnaire
        """
        user_id = req.get_param("user_id", required=True)
        user = User.get_one(user_id)
        user.update(**user_creation.json_response)
        
        resp.media = user.json_response



    def on_delete(self, req, resp):
        """DELETE /users/{userid}/
            params: formid

            Returns: Questions for the requested questionnaire
        """
        user_id = req.get_param("user_id", required=True)
        user = User.get_one(user_id)
        user.delete()

        resp.media = user.json_response


class UsersListManager:
    def on_get(self, req, resp):
        """GET /users/all/
            params: formid

            Returns: Questions for the requested questionnaire
        """
        resp.media =  [x.as_dict for x in User.get_all()]



