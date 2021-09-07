from sqlalchemy import (
    create_engine,
    MetaData,
)
from sqlalchemy.orm import (
    declarative_base,
)
from fixture import (
    SQLAlchemyFixture,
    DataSet,
)

from models import (
    Phone,
    Users,
    SQLALCHEMY_DATABASE_URI,
)

Base = declarative_base()
Session = None


class PhoneData(DataSet):
    class first_phone:
        phone_id = 1
        number = "+799900000000"

    class second_phone:
        phone_id = 2
        number = "+79990000100"

class UserData(DataSet):
    class user_first:
        user_id = 1
        name = "Ваня"
        surname = "Андреев"
        date_birth = '1998-08-09'
        phone_id = PhoneData.first_phone.phone_id

    class user_second:
        user_id = 2
        name = "Ваня"
        surname = "Валеев"
        date_birth = '1998-08-09'
        phone_id = PhoneData.first_phone.phone_id

    class user_third:
        user_id = 3
        name = "Ваня"
        surname = "Горин"
        date_birth = '1998-08-09'
        phone_id = PhoneData.second_phone.phone_id

def load_data():
    engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
    conn = engine.connect()
    metadata = MetaData()
    metadata.bind = engine
    dbfixture = SQLAlchemyFixture(
        env={'PhoneData': Phone, 'UserData': Users},
        engine=metadata.bind
    )

    data = dbfixture.data(PhoneData, UserData)
    data.setup()
    conn.close()

if __name__ == '__main__':
    load_data()
