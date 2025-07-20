from datetime import datetime

from sqlmodel import Field, SQLModel, create_engine, Session, Relationship, delete

sqlite_filename = "database.db"
sqlite_url = f"sqlite:///{sqlite_filename}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session


class MealFoodLink(SQLModel, table=True):
    """Food to Meal mapping."""
    meal_id: int = Field(index=True, foreign_key="meal.id", primary_key=True)
    food_id: int = Field(foreign_key="food.id", primary_key=True)


class MealBase(SQLModel):
    """Base model for Meals."""
    eaten_at: datetime = Field(default=datetime.now())


class Meal(MealBase, table=True):
    """Data about a specific meal."""
    id: int | None = Field(default=None, primary_key=True)

    foods: list["Food"] = Relationship(back_populates="meals", link_model=MealFoodLink)


class FoodBase(SQLModel):
    """Base model for Foods."""
    name: str
    calories: int


class Food(FoodBase, table=True):
    """Data about a specific food item."""
    id: int = Field(primary_key=True)

    meals: list[Meal] = Relationship(back_populates="foods", link_model=MealFoodLink)


class MealPublic(SQLModel):
    """Data about a meal to be returned to the client"""
    meal: Meal
    foods: list[Food]


class MealPublicList(SQLModel):
    """Full list of meal information."""
    meals: list[MealPublic]


def create_test_data():
    with Session(engine) as session:
        food_1 = Food(name="Hamburger", calories=300)
        food_2 = Food(name="French Fries", calories=280)
        food_3 = Food(name="Cereal", calories=350)
        food_4 = Food(name="Milk", calories=170)
        food_5 = Food(name="Peanut Butter & Jelly Sandwich", calories=600)

        meal_1 = Meal(eaten_at=datetime(2025, 7, 16, 8, 30), foods=[food_3, food_4])
        meal_2 = Meal(eaten_at=datetime(2025, 7, 16, 12, 30), foods=[food_5])
        meal_3 = Meal(eaten_at=datetime(2025, 7, 16, 18, 00), foods=[food_1, food_2])

        session.add(food_1)
        session.add(food_2)
        session.add(food_3)
        session.add(food_4)
        session.add(food_5)
        session.add(meal_1)
        session.add(meal_2)
        session.add(meal_3)
        session.commit()

        session.refresh(food_1)
        session.refresh(food_2)
        session.refresh(food_3)
        session.refresh(food_4)
        session.refresh(food_5)
        session.refresh(meal_1)
        session.refresh(meal_2)
        session.refresh(meal_3)


def delete_test_data():
    with Session(engine) as session:
        session.exec(delete(MealFoodLink))
        session.exec(delete(Food))
        session.exec(delete(Meal))
        session.commit()