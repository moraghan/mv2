from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select

class Request(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    request_type: str
    request_url: str
    response_status: int
    response_text: str

from helper import get_db_connection, get_api_key, get_request_types

REQUEST_TYPE_INFO = get_request_types()
API_KEY = get_api_key()
DB_URL = get_db_connection()

request_1 = Request(request_type="movie", request_url="apple.com",response_status=200,response_text='{"a":2,"c":[4,5,{"f":7}]}')



engine = create_engine("sqlite:///database.db")


SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    session.add(request_1)
    session.commit()

