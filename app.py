from flask import render_template
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin
import json
# fuzzy distance algorithm
from fuzzywuzzy import fuzz

# image match
from image_match.goldberg import ImageSignature
gis = ImageSignature()

# init app
app = Flask(__name__)
api = Api(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Create a URL route in our application for "/"
@app.route('/')
def hello():
    return 'Hello !'

@app.route('/api/match', methods=['GET'])
def matchImage():
    img1 = request.args.get('img1')
    img2 = request.args.get('img2')
    a = gis.generate_signature('{}'.format(img1))
    b = gis.generate_signature('{}'.format(img2))
    return {"score":gis.normalized_distance(a, b)}

@app.route('/api/matchs', methods=['GET'])
def matchImages():
    img1 = request.args.get('img1')
    imgs = request.args.getlist('imgs')
    a = gis.generate_signature('{}'.format(img1))
    scores = []
    # calculate the matching score for each item in the list
    for img in imgs:
        b = gis.generate_signature(img)
        res = gis.normalized_distance(a, b)
        scores.append({"image":img, "score": res})
    # score
    return {"_source": img1, "scores": scores}

@app.route('/api/matching', methods=['GET'])
def matching():
    # the json object
    compare = request.get_json()
    # source product - amazom
    amazom = compare['source_product']
    # list of mlms to compare with
    mlms = compare['mlms']
    # signature for the product image
    a = gis.generate_signature(amazom['image'])
    scores = []
    for mlm in mlms:
        # score image
        b = gis.generate_signature(mlm['image'])
        imgScore = 1 - gis.normalized_distance(a, b)
        # comparing text
        nameScore = fuzz.token_set_ratio(amazom['name'], mlm['name']) / 100

        # calculate the match score
        matchScore = (imgScore + nameScore) / 2

        # store result
        scores.append({"product": mlm, "scores":{"img-score": imgScore, "title-score": nameScore}, "match-score":matchScore})

    return {"_source": amazom, "scores": scores}

# error handling
@app.errorhandler(404)
def notfound():
    return {"404":"No route specified !"}

@app.errorhandler(500)
def notfound():
    return {"500":"No route specified !"}

if __name__ == '__main__':
     app.run()
