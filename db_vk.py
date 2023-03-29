from pprint import pprint

from sqlalchemy import Column, Integer, String, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, InvalidRequestError

DSN = 'postgresql+psycopg2://slava:7548@localhost:5432/vk_db_'

Base = declarative_base()
engine = create_engine(DSN)
connection = engine.connect()
Session = sessionmaker(bind=engine)

# User бота VK
class User(Base):

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    vk_id = Column(Integer, unique=True)

# Информация о второй половинке добавленная в избранное
class Second_half(Base):

    __tablename__ = 'second_half'
    id = Column(Integer, primary_key=True, autoincrement=True)
    vk_id = Column(Integer, unique=True)
    name = Column(String)
    surname = Column(String)
    gender = Column(Integer)
    year = Column(Integer)
    city = Column(String)
    link = Column(String)
    photo = Column(String)
    id_user = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))

Base.metadata.create_all(engine)

# Функции______________________________________

session = Session()

#1 Регистрация пользователя
def register_user(vk_id):

    try:
        new_user = User(vk_id=vk_id)
        session.add(new_user)
        session.commit()
        return True

    except (IntegrityError, InvalidRequestError):
        return False

#2 Проверка регистрации пользователя бота в БД
def check_db_reg(ids):

    current_user_id = session.query(User).filter_by(vk_id=ids).first()
    return current_user_id

#3 Проверка Userа в БД
def check_db_user(ids):

    second_half_user = session.query(Second_half).filter_by(vk_id=ids).first()
    return second_half_user

#4 Проверка Userа в избранном
def check_db_elit(ids):

    current_users_id = session.query(User).filter_by(vk_id=ids).first()
    alls_users = session.query(Second_half).filter_by(id_user=current_users_id.id).all()
    return alls_users

#5 Удаляет Userа из избранного
def delete_db_elit(ids):

    current_user = session.query(Second_half).filter_by(vk_id=ids).first()
    session.delete(current_user)
    session.commit()

#6 Сохраняем нужного пользователя в БД
def add_user(vk_id, name, surname, gender, year, city, link, photo, id_user):

    try:
        new_user = Second_half(
            vk_id=vk_id,
            name=name,
            surname=surname,
            gender=gender,
            year=year,
            city=city,
            link=link,
            photo=photo,
            id_user=id_user
        )
        session.add(new_user)
        session.commit()
        return True
    except (IntegrityError, InvalidRequestError):
        return False

#6 Список избранное
def list_favorite():

    list_users = []
    users = session.query(Second_half).all()

    for user in users:
        pers = {'id': user.id, 'vk_id': user.vk_id, 'name': user.name, 'surname': user.surname, 'link': user.link, 'photo': user.photo}
        list_users.append(pers)
    return list_users


list_favorite()
# print(check_db_reg(524766546).id)
# print(check_db_reg(524766546))








