from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@db:3306/car'
db = SQLAlchemy(app)

class Car(db.Model):
    __tablename__ = "cars"
    id = db.Column(db.Integer, primary_key=True)
    maker = db.Column(db.String(20))
    model = db.Column(db.String(20))
    year = db.Column(db.String(20))
    cartype = db.Column(db.String(20))

    def create(self):
      db.session.add(self)
      db.session.commit()
      return self
    def __init__(self,maker,model,year,cartype):
        self.maker = maker
        self.model = model
        self.year = year
        self.cartype = cartype
    def __repr__(self):
        return '' % self.id

while True:
    try:
        db.create_all()
        break
    except Exception as e:
        print("db connection failure!")
        time.sleep(5)

class CarSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Car
        sqla_session = db.session
    id = fields.Number(dump_only=True)
    maker = fields.String(required=True)
    model = fields.String(required=True)
    year = fields.String(required=True)
    cartype = fields.String(required=True)

@app.route('/cars', methods = ['GET'])
def index():
    get_cars = Car.query.all()
    car_schema = CarSchema(many=True)
    cars = car_schema.dump(get_cars)
    return make_response(jsonify({"car": cars}))

@app.route('/cars/<id>', methods = ['GET'])
def get_car_by_id(id):
    get_car = Car.query.get(id)
    car_schema = CarSchema()
    car = car_schema.dump(get_car)
    return make_response(jsonify({"car": car}))

@app.route('/cars/<id>', methods = ['PUT'])
def update_car_by_id(id):
    data = request.get_json(force = True)
    get_car = Car.query.get(id)
    if data.get('maker'):
        get_car.maker = data['maker']
    if data.get('model'):
        get_car.model = data['model']
    if data.get('year'):
        get_car.year = data['year']
    if data.get('cartype'):
        get_car.cartype= data['cartype']    
    db.session.add(get_car)
    db.session.commit()
    car_schema = CarSchema(only=['id', 'maker', 'model','year','cartype'])
    car = car_schema.dump(get_car)
    return make_response(jsonify({"car": car}))

@app.route('/cars/<id>', methods = ['DELETE'])
def delete_car_by_id(id):
    get_car = Car.query.get(id)
    db.session.delete(get_car)
    db.session.commit()
    return make_response("",204)

@app.route('/cars', methods = ['POST'])
def create_car():
    data = request.get_json(force = True)
    car_schema = CarSchema()
    car = car_schema.load(data)
    result = car_schema.dump(car.create())
    return make_response(jsonify({"car": result}),200)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
