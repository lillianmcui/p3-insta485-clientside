"""Views, one for each Insta485 page."""
from insta485.views.index import show_index
from insta485.views.user import show_user
from insta485.views.uploads import download_file
from insta485.views.likes import update_likes
from insta485.views.user import show_followers
from insta485.views.user import show_following
from insta485.views.account import show_login
from insta485.views.account import show_create
from insta485.views.account import show_delete
from insta485.views.account import show_edit
from insta485.views.index import show_explore
from insta485.views.index import show_post
from insta485.views.likes import show_comments
from insta485.views.user import update_following
