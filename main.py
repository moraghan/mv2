from typing import Optional
import requests
import json

from sqlmodel import Field, Session, SQLModel, create_engine, select

class Request(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    request_type: str
    request_id: int
    request_url: str
    response_status: int
    response_text: Optional[str]

from helper import get_db_connection, get_api_key, get_request_types

engine = create_engine("sqlite:///database.db")

SQLModel.metadata.create_all(engine)

REQUEST_TYPE_INFO = get_request_types()
API_KEY = get_api_key()

request_url = REQUEST_TYPE_INFO['movie'].URL
current_key = 100

while current_key <= 100000:

        enriched_url = request_url.replace('{api_key}', API_KEY).replace('{id}', str(current_key))

        _response_data = requests.get(enriched_url)

        if _response_data.status_code == 200:
            response_data = _response_data.text
        else:
            response_data ='Error'

        request_1 = Request(request_type="movie",
                        request_url=enriched_url,
                        request_id=current_key,
                        response_status=_response_data.status_code,
                        response_text=response_data)


        with Session(engine) as session:
            session.add(request_1)
            session.commit()

        current_key = current_key + 1

