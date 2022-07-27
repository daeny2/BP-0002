from flask import request, redirect, jsonify, make_response
from flask_restx import Resource

from ..util.dto import UserDto
import requests

#from ..service.users import post_login, post_logout, social_signin, post_signup, get_find_id, edit_temp_pw, get_find_user, get_email_check, get_user_info, edit_user_info, get_first_loading
from ..service.users import save_new_user, get_all_users, get_a_user

#from ..config import kakao_client_id

api = UserDto.api
_user = UserDto.user


@api.route('/')
class UserList(Resource):
    @api.doc('list_of_registered_users')
    @api.marshal_list_with(_user, envelope='data')
    def get(self):
        """List all registered users"""
        return get_all_users()
 
    @api.expect(_user, validate=True)
    @api.response(201, 'User successfully created.')
    @api.doc('create a new user')
    def post(self):
        """Creates a new User """
        data = request.json
        return save_new_user(data=data)
 
 
@api.route('/<id>')
@api.param('id', 'The User identifier')
@api.response(404, 'User not found.')
class User(Resource):
    @api.doc('get a user')
    @api.marshal_with(_user)
    def get(self, id):
        """get a user given its identifier"""
        user = get_a_user(id)
        if not user:
            api.abort(404)
        else:
            return user

"""
@api.route('')
class UserInfo(Resource):
    def get(self):
        #Get User Info for MyPage
        return get_user_info()
        
    def patch(self):
        #Edit user info
        data = request.get_json().get('users')
        return edit_user_info(data)

@api.route('/id')
class GetFindUser(Resource):
    def get(self):
        #Get User Id and Send temporary password
        data = request.args.to_dict()
        return get_find_user(data)

@api.route('/password')
class EditPassword(Resource):
    def patch(self):
        #Edit temporary password
        data = request.get_json().get('users')
        return edit_temp_pw(data)

@api.route('/email')
class GetFindID(Resource):
    def get(self):
        #Get Find ID
        data = request.args.to_dict()
        if 'email' in data.keys():
            return get_email_check(data)
        else:
            return get_find_id(data)

@api.route('/signup')
class PostSignup(Resource):
    def post(self):
        #Post Signup
        data = request.get_json().get('users')
        return post_signup(data)

@api.route('/login')
class PostLogin(Resource):
    def post(self):
        #Post Login
        data = request.get_json().get('users')
        return post_login(data)

@api.route('/logout')
class PostLogout(Resource):
    def post(self):
        #Post Logout
        data = request.get_json().get('users')
        return post_logout(data)


@api.route("/oauth/kakao") 
class KakaoSignIn(Resource):
    def get(self):
        client_id = kakao_client_id
        redirect_uri = "http://127.0.0.1:5000/users/oauth/kakao/callback"
        kakao_oauthurl = f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
        return redirect(kakao_oauthurl)


@api.route("/oauth/kakao/callback") 
class KakaoSignInCallback(Resource):
    def get(self):
        #print("request.GET :" , request.args.get)
        try:
            code = request.args.get("code")                                 
            client_id = kakao_client_id
            redirect_uri = "http://127.0.0.1:5000/users/oauth/kakao/callback"
            
            token_request = requests.get(                                       
                f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={redirect_uri}&code={code}"
            )
            
            token_json = token_request.json() 

            error = token_json.get("error",None)

            if error is not None :
                return make_response({"message": "INVALID_CODE"}, 400) 

            access_token = token_json.get("access_token") 
            #print("access_token:", access_token)                       

            profile_request = requests.get(
                    "https://kapi.kakao.com/v2/user/me", headers={"Authorization" : f"Bearer {access_token}"},
                )
            data = profile_request.json()
            # 위의 코드로 이번엔 카카오에서 유저 정보를 담은 url에 access token을 담아서, 유저 정보를 겟 요청합니다.

        except KeyError:
            return make_response({"message" : "INVALID_TOKEN"}, 400)

        except access_token.DoesNotExist:
            return make_response({"message" : "INVALID_TOKEN"}, 400)

        return social_signin(data=data) # 이젠 위에서 받은 데이터를 DB에 넣어줘야 합니다. 이 과정이 service에서 진행됩니다.

@api.route('/isloading')
class FirstLoading(Resource):
    def get(self):
        """Check Server is Ready"""
        return get_first_loading()
"""        