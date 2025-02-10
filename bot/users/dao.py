from database.dao.base import BaseDAO
from users.model import User


class UserDAO(BaseDAO):
    model = User
