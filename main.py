from contextlib import asynccontextmanager
import logging
from typing import Annotated

from fastapi import FastAPI, Depends
from fastapi.templating import Jinja2Templates
from fasthx.jinja import Jinja

from model import Meal, Food, MealPublic, MealPublicList, create_db_and_tables, get_session, create_test_data, delete_test_data
from sqlmodel import Session, select


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger(__name__)

logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

SessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    create_test_data()
    yield
    delete_test_data()


app = FastAPI(lifespan=lifespan)
jinja = Jinja(Jinja2Templates("templates"))

@app.get("/")
@jinja.page("index.html")
async def root() -> None:
    ...


@app.get("/food/", response_model=list[Food])
async def read_foods(session: SessionDep, offset: int = 0, limit: int = 100):
    foods = session.exec(select(Food).offset(offset).limit(limit)).all()
    return foods


@app.get("/food/{food_id}", response_model=Food)
async def read_food(food_id: int, session: SessionDep):
    result = session.exec(select(Food).where(Food.id==food_id)).first()

    return result


@app.post("/food/", response_model=Food)
async def create_food(food: Food, session: SessionDep):
    session.add(food)
    session.commit()
    session.refresh(food)
    return food


@app.get("/meal/", response_model=MealPublicList)
@jinja.hx("meal-list.html")
async def read_meals(session: SessionDep, offset: int = 0, limit: int = 100):
    results = session.exec(select(Meal).offset(offset).limit(limit)).all()
    meals: list[MealPublic] = []
    for res in results:
        meals.append(MealPublic(meal=res, foods=res.foods))

    return MealPublicList(meals=meals)


@app.get("/meal/{meal_id}", response_model=MealPublic)
async def read_meal(meal_id: int, session: SessionDep):
    result = session.exec(select(Meal).where(Meal.id==meal_id)).first()

    return MealPublic(meal=result, foods=result.foods)
