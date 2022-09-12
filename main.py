from typing import Optional
import requests
from datetime import datetime, date
import json
from pydantic import condecimal
from sqlmodel import Field, Session, SQLModel, create_engine, select


class Request(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    request_type: str
    request_id: int
    request_url: str
    response_status: int
    response_text: Optional[str]


class Movie(SQLModel, table=True):
    movie_id: int = Field(default=None, primary_key=True)
    movie_title: str = Field(nullable=False, max_length=100)
    imdb_id: str = Field(nullable=False, max_length=10)
    release_date: date = Field(nullable=True)
    runtime_mins: int
    budget: condecimal(max_digits=20, decimal_places=2) = Field(default=0)
    revenue: condecimal(max_digits=20, decimal_places=2) = Field(default=0)
    language: str = Field(max_length=5)
    overview: str = Field(max_length=1000)
    tagline: str = Field(max_length=255)
    status: str = Field(max_length=10)
    vote_average: condecimal(max_digits=5, decimal_places=2) = Field(default=0)
    vote_count: int
    popularity: condecimal(max_digits=5, decimal_places=2) = Field(default=0)
    updated_on: datetime = Field(default=datetime.now())


from helper import get_db_connection, get_api_key, get_request_types

engine = create_engine("sqlite:///database.db")

SQLModel.metadata.create_all(engine)

REQUEST_TYPE_INFO = get_request_types()
API_KEY = get_api_key()

request_url = REQUEST_TYPE_INFO['movie'].URL
current_key = 100

with Session(engine) as session:
    while current_key <= 100000:
        enriched_url = request_url.replace('{api_key}', API_KEY).replace('{id}', str(current_key))
        _response_data = requests.get(enriched_url)

        if _response_data.status_code == 200:
            response_data = _response_data.json()
            if session.query(Movie).filter(Movie.movie_id == response_data['id']).first() is None:
                movie_to_add = Movie(

                    movie_id=response_data['id'],
                    movie_title=response_data['title'],
                    imdb_id=response_data['imdb_id'],
                    release_date=response_data['release_date'] or None,
                    runtime_mins=response_data['runtime'],
                    budget=response_data['budget'] or None,
                    revenue=response_data['revenue'] or None,
                    language=response_data['original_language'],
                    overview=response_data['overview'],
                    tagline=response_data['tagline'],
                    status=response_data['status'],
                    vote_average=response_data['vote_average'],
                    vote_count=response_data['vote_count'],
                    popularity=response_data['popularity']
                )
                session.add(movie_to_add)
        else:
            response_data = 'Error'

        request_1 = Request(request_type="movie",
                            request_url=enriched_url,
                            request_id=current_key,
                            response_status=_response_data.status_code,
                            response_text=response_data)

        session.add(request_1)
        session.commit()

        current_key = current_key + 1
        print(current_key)
session.commit()
