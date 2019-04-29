from flask import Flask, jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from datetime import datetime, timedelta
import re
import json

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "eska.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Init db
db = SQLAlchemy(app)

# Init ma
ma = Marshmallow(app)


# Eksa Hits Class/Model
class Hits(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    title_url = db.Column(db.String(240), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"), nullable=False)
    artist = db.relationship("Artists", back_populates="hits", lazy=True)

    def __repr__(self):
        return f"Hits({self.id}, {self.title}, {self.created_at})"


# Hits schema
class HitsSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "title_url")  # "created_at", "updated_at", "artist_id"


# Init  Hits schema
hit_schema = HitsSchema(strict=True)
hits_schema = HitsSchema(many=True, strict=True)


# Artists Class/Model
class Artists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    hits = db.relationship("Hits", backref="artists", lazy=True)

    def __repr__(self):
        return f"Artists({self.id}, {self.first_name}, {self.last_name})"


# Artists schema
class ArtistsSchema(ma.Schema):
    class Meta:
        fields = ("id", "first_name", "last_name", "created_at")


# Init Artists schema
artist_schema = ArtistsSchema(strict=True)
artists_schema = ArtistsSchema(many=True, strict=True)


# get list of 20 eska hits ordered by creation date
@app.route("/api/v1/hits", methods=["GET"])
def get_hits():

    newest_20_hits = Hits.query.order_by("created_at").limit(20)
    result = hits_schema.dump(newest_20_hits)
    return jsonify(result.data)


# get hit details
@app.route("/api/v1/hits/<title_url>", methods=["GET"])
def get_hit(title_url):

    # get hit query object filtered by the title_url

    query_hit = Hits.query.filter_by(title_url=title_url)
    # get Hits Class object by pk
    try:
        hit = Hits.query.get(query_hit[0].id)
    except IndexError:
        return not_found("This title doesn't exist")
    # get arists data if exists
    if hit.artists is not None:
        artist = {
            "id": hit.artists.id,
            "first_name": hit.artists.first_name,
            "last_name": hit.artists.last_name,
        }
    else:
        artist = "Not in db"

    hit_data = hit_schema.dump(hit)

    result = {"hit": hit_data.data, "artist": artist}
    # returning flask.Response() object
    return jsonify(result)  # artist_data


@app.route("/api/v1/hits", methods=["POST"])
def create_hit():
    """
    Receives JSON format data containing hit title and artist_id. Validates data.
    Inserts data into db.

    :return:
    flask.Response() object
    """
    if validate_json() == "Bad JSON":
        return wrong_data("JSON has an error")

    if title_and_artist_id_provided(request.json) is None:
        return wrong_data("please provide json data with (title) and (artist_id)")
    if validate_title(request.json) is None:
        return wrong_data("title must be a non empty string containing only"
                          " letters ans spaces")
    if artist_id_is_int(request.json) is None:
        return wrong_data("artist_id must be an integer")

    artist_id = request.json["artist_id"]
    title = request.json["title"].strip()
    new_hit = Hits(
        artist_id=artist_id,
        title=title,
        created_at=get_timestamp(),
        title_url=urlify(title),
    )

    db.session.add(new_hit)
    db.session.commit()

    return hit_schema.jsonify(new_hit), 201


@app.route("/api/v1/hits/<title_url>", methods=["PUT"])
def update_hit(title_url):
    """
        Receives JSON format data which can contains fields like hit title and artist_id.
        Querying db for hit to update.
        Validates data.
        Updating data into db.

        :return:
        flask.Response() object
        """
    if validate_json() == "Bad JSON":
        return wrong_data("JSON has an error")
    # get hit filtered by the title_url
    query_hit = Hits.query.filter_by(title_url=title_url)
    # get hit filtered by the title_url
    try:
        hit = Hits.query.get(query_hit[0].id)
    except IndexError:
        return not_found("This title doesn't exist")

    # validation
    if not request.json:
        return wrong_data("You didn't send anything to update")
    if 'title' in request.json and validate_title(request.json) is None:
        return wrong_data("title must be a non empty string containing only"
                          " letters ans spaces")
    if "artist_id" in request.json and artist_id_is_int(request.json) is None:
        return wrong_data("artist_id must be an integer")

    # saving data to db
    hit.title = request.json.get("title", hit.title)
    hit.artist_id = request.json.get("artist_id", hit.artist_id)
    hit.title_url = urlify(hit.title)
    hit.updated_at = get_timestamp()

    db.session.commit()

    return hit_schema.jsonify(hit), 201


@app.route("/api/v1/hits/<title_url>", methods=["DELETE"])
def delete_hit(title_url):
    # get hit filtered by the title_url
    query_hit = Hits.query.filter_by(title_url=title_url)
    # get hit filtered by the title_url
    try:
        hit = Hits.query.get(query_hit[0].id)
    except IndexError:
        return not_found("This title doesn't exist")

    # delete record
    db.session.delete(hit)
    db.session.commit()

    return hit_schema.jsonify(hit), 202


def get_timestamp():
    return datetime.utcnow() + timedelta(hours=2)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": error}), 404)


@app.errorhandler(400)
def wrong_data(error):
    return make_response(jsonify({"error": error}), 400)


# conver string to the form accepted by an url
def urlify(s):

    # Remove all non-word characters (everything except numbers and letters)
    s = re.sub(r"[^\w\s-]", "", s).strip()

    # Replace all runs of whitespace with a single dash
    s = re.sub(r"\s+", "-", s)

    return s


def validate_json():
    try:
        json.loads(request.data)
    except json.decoder.JSONDecodeError:
        return "Bad JSON"


# check if title and aritst_id in request.json
def title_and_artist_id_provided(request_json):
    if request_json and "title" in request_json and "artist_id" in request_json:
        return True


# check if title contains only alpha or space characters and is not empty
def validate_title(request_json):
    if isinstance(request_json["title"], str) and \
            any(x.isalpha() for x in request_json['title']) and \
            all(x.isalpha() or x.isspace() for x in request_json["title"]):
            return True


# validate artist_id
def artist_id_is_int(request_json):
    if isinstance(request_json["artist_id"], int):
        return True


# Run server
if __name__ == "__main__":
    app.run(debug=True)
