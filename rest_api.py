#!/usr/bin/python3
import traceback

from flask import Flask, jsonify, request
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost/savvaclub'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

api = Api(app)
db = SQLAlchemy(app)


class ReceiptDB(db.Model):
    __tablename__ = 'receipts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    avatar = db.Column(db.String())
    description = db.Column(db.String())
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)

    def __init__(self, id, name, avatar, description, product_id):
        self.id = id
        self.name = name
        self.avatar = avatar
        self.description = description,
        self.product_id = product_id

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'avatar': self.avatar,
            'description': self.description,
            'product_id': self.product_id
        }

    def __repr__(self):
        return jsonify(self.serialize())


class ProductDB(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String())
    price = db.Column(db.Float)
    thumb = db.Column(db.String())
    image = db.Column(db.String())
    description = db.Column(db.String())
    slug = db.Column(db.String())
    measuring = db.Column(db.String())
    url = db.Column(db.String())
    receipts = db.relationship("ReceiptDB", backref="product", lazy='dynamic')

    def __init__(self, name, price, thumb, image, descrition, slug, measuring, url):
        self.name = name
        self.price = price
        self.thumb = thumb
        self.image = image
        self.description = descrition
        self.slug = slug
        self.measuring = measuring
        self.url = url
        # self.receipts = receipts

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'thumb': self.thumb,
            'image': self.image,
            'description': self.description,
            'slug': self.slug,
            'measuring': self.measuring,
            'url': self.url,
            'receipts': [item.serialize() for item in self.receipts]
        }

    def __repr__(self):
        return jsonify(self.serialize())


# class Products(Resource):
@app.route("/api/v2/shop/products/<string:category>/<int:page>")
def get_products(category, page):
    try:
        # request.
        return jsonify({'data': [item.serialize() for item in ProductDB.query.all()]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# curl --location --request PUT 'https://127.0.0.1:5000/api/v2/shop/products' \
# --header 'accept: application/json' \
# --header 'Content-Type: application/json' \
# --data-raw '{
# 	"name": "Book 2",
#     "price": 102.0,
# 	"thumb": "",
#     "image": "",
#     "description": "Some book2",
# 	"slug": "",
#     "measuring":"",
#     "url": ""
# }'
@app.route("/api/v2/shop/products", methods=['PUT'])
def put_products():
    try:
        print("\nRun request: %s" % (request))
        print(request.headers)
        print(request.json)
        print("<== END ==>: %s" % (request))
        if request.json is not None \
                and 'name' in request.json.keys() \
                and 'price' in request.json.keys() \
                and 'thumb' in request.json.keys() \
                and 'image' in request.json.keys() \
                and 'description' in request.json.keys() \
                and 'slug' in request.json.keys() \
                and 'measuring' in request.json.keys() \
                and 'url' in request.json.keys():
            db.session.add(ProductDB(
                request.json['name'],
                request.json['price'],
                request.json['thumb'],
                request.json['image'],
                request.json['description'],
                request.json['slug'],
                request.json['measuring'],
                request.json['url']
            ))
            db.session.commit()
            return jsonify({'result': 'ok'})
        else:
            return jsonify({'result': 'can\'t find id'}), 400

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# curl --location --request PATCH 'https://127.0.0.1:5000/api/v2/shop/products' \
# --header 'accept: application/json' \
# --header 'Content-Type: application/json' \
# --data-raw '{
#   "id": 1
# 	"name": "Book 2",
#     "price": 102.0,
# 	"thumb": "",
#     "image": "",
#     "description": "Some book2",
# 	"slug": "",
#     "measuring":"",
#     "url": ""
# }'
@app.route("/api/v2/shop/products", methods=['PATCH'])
def patch_products():
    try:
        print("\nRun request: %s" % (request))
        print(request.headers)
        print(request.json)
        print("<== END ==>: %s" % (request))

        if request.json is not None and 'id' in request.json.keys:
            product = ProductDB.query.filter(ProductDB.id == request.json['id'])
            if product is not None:
                if 'name' in request.json.keys(): product.name = request.json['name']
                if 'price' in request.json.keys(): product.price = request.json['price']
                if 'thumb' in request.json.keys(): product.thumb = request.json['thumb']
                if 'image' in request.json.keys(): product.image = request.json['image']
                if 'description' in request.json.keys(): product.description = request.json['description']
                if 'slug' in request.json.keys(): product.slug = request.json['slug']
                if 'measuring' in request.json.keys(): product.measuring = request.json['measuring']
                if 'url' in request.json.keys(): product.url = request.json['url']

                db.session.save(ProductDB(
                    request.json['name'],
                    request.json['price'],
                    request.json['thumb'],
                    request.json['image'],
                    request.json['description'],
                    request.json['slug'],
                    request.json['measuring'],
                    request.json['url']
                ))
                db.session.commit()
                return jsonify({'result': 'ok'}), 204
            else:
                return jsonify({'result': 'item not found'}), 403
        else:
            return jsonify({'result': 'can\'t find id'}), 400

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# curl -k -X DELETE "https://127.0.0.1:5000/api/v2/shop/products" \
# -H "accept: application/json"\
# -H "Content-Type: application/json"\
# -d "{ \"id\": 1}"
@app.route("/api/v2/shop/products", methods=['DELETE'])
def delete_products():
    try:
        print("\nRun request: %s" % (request))
        print(request.headers)
        print(request.json)
        print("<== END ==>: %s" % (request))
        if request.json is not None and 'id' in request.json.keys():
            ProductDB.query.filter(ProductDB.id == request.json['id']).delete()
            db.session.commit()
            return jsonify({'result': 'ok'})
        else:
            return jsonify({'result': 'can\'t find id'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/version", methods=['GET', 'PUT', 'PATCH', 'DELETE', 'POST'])
def get_version():
    return jsonify({'version': '1.0.0', 'title': 'simple sample rest api'})


if __name__ == '__main__':
    app.run(host='192.168.1.22', debug=True, ssl_context=('cert.pem', 'key.pem'), port=5001)
