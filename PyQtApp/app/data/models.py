from sqlalchemy import (
    Integer,
    String,
    Column,
    create_engine,
    Boolean,
    ForeignKey,
    Date,
)
from sqlalchemy.orm import (
    declarative_base,
    column_property,
    relationship,
    sessionmaker,
)

Base = declarative_base()
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:789456@localhost/list_phones'

engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
Session = sessionmaker(bind=engine)


def connect_db():
    engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
    Base.metadata.create_all(engine)

class UserProfile(Base):
    __tablename__ = 'userprofile'
    user_id = Column(Integer, primary_key=True)
    login = Column(String(40), nullable=False)
    password = Column(String(123), nullable=False)
    date_birth = Column(Date, index=True)
    state_auth = Column(Boolean, default=False, nullable=False)


class Users(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    surname = Column(String(40), nullable=False)
    name = Column(String(40), nullable=False)
    fullname = column_property(surname + ' ' + name + ' ')
    date_birth = Column(Date, index=True)
    phone_id = Column(Integer, ForeignKey('phones.phone_id', ondelete='CASCADE'))
    phone = relationship('Phone', back_populates='user')


class Phone(Base):
    __tablename__ = 'phones'
    phone_id = Column(Integer, primary_key=True)
    number = Column(String(40), unique=True, nullable=True)
    user = relationship('Users', back_populates='phone')


if __name__ == '__main__':
    connect_db()
