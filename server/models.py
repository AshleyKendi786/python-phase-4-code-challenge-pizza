

   
    from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    _tablename_ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

    # relationships
    restaurant_pizzas = db.relationship(
        "RestaurantPizza",
        back_populates="restaurant",
        cascade="all, delete-orphan"
    )
    pizzas = association_proxy("restaurant_pizzas", "pizza")

    # serialization rules (prevent recursion)
    serialize_rules = ("-restaurant_pizzas.restaurant", "-restaurant_pizzas.pizza")

    def _repr_(self):
        return f"<Restaurant id={self.id} name={self.name}>"


class Pizza(db.Model, SerializerMixin):
    _tablename_ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)

    # relationships
    restaurant_pizzas = db.relationship(
        "RestaurantPizza",
        back_populates="pizza",
        cascade="all, delete-orphan"
    )
    restaurants = association_proxy("restaurant_pizzas", "restaurant")

    # serialization rules (prevent recursion)
    serialize_rules = ("-restaurant_pizzas.pizza", "-restaurant_pizzas.restaurant")

    def _repr_(self):
        return f"<Pizza id={self.id} name={self.name}>"


class RestaurantPizza(db.Model, SerializerMixin):
    _tablename_ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    # foreign keys
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id"), nullable=False)

    # relationships
    restaurant = db.relationship("Restaurant", back_populates="restaurant_pizzas")
    pizza = db.relationship("Pizza", back_populates="restaurant_pizzas")

    # serialization rules (prevent recursion)
    serialize_rules = ("-restaurant.restaurant_pizzas", "-pizza.restaurant_pizzas")

    # validations
    @validates("price")
    def validate_price(self, key, price):
        if price is None:
            raise ValueError("Price is required")
        if price < 1 or price > 30:
            raise ValueError("Price must be between 1 and 30")
        return price

    def _repr_(self):
        return f"<RestaurantPizza id={self.id} price=${self.price}>"
