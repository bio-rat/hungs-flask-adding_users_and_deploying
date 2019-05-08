from flask import Flask, redirect, url_for, flash, render_template, jsonify, request
from flask_login import login_required, logout_user, current_user 
from .config import Config
from .models import db, login_manager, Excerpt, Score, Token
from .oauth import blueprint
from .cli import create_db
from flask_migrate import Migrate
from flask_cors import CORS



app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(blueprint, url_prefix="/login")
app.cli.add_command(create_db)
db.init_app(app)
migrate = Migrate(app, db)
login_manager.init_app(app)
CORS(app)


@app.route("/logout")
@login_required
def logout():
    Token.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    logout_user()
    flash("You have logged out")
    return redirect(url_for("index"))


@app.route("/")
def index():
    return render_template("home.html")

@app.route('/test')
@login_required
def test():
  return jsonify({
      "success": True, 
      "user_id": current_user.id, 
      "user_name": current_user.name})

@app.route('/score', methods=['POST'])
@login_required
def create():
  x = request.get_json()

  score = Score(wpm = x['wpm'], excerpt_id=x['excerpt_id'], user_id=current_user.id)

  db.session.add(score)
  db.session.commit()

  # find the current excerpt
  excerpt = Excerpt.query.filter_by(id=x['excerpt_id']).first()

  # count total score
  total_scores = excerpt.scores.count()

  # find all the score of excerpts_id
  scores = excerpt.scores.order_by(Score.wpm.desc()).all()
  
  # make wpm list
  ranking_list = []

  for score in scores:
    ranking_list.append(score.wpm)

  # find the rank through wpm list
  ranking = ranking_list.index(x['wpm']) + 1

  return jsonify({
    "success": True,
    "ranking": ranking,
    "total_scores": total_scores,
  }), 201


@app.route('/excerpts/random', methods=['GET'])
@login_required
def random_excerpt():

    # get random excerpt
    excerpt = Excerpt.query.order_by(db.func.random()).first()

    # total scores
    scores_count = excerpt.scores.count()

    # all the scores
    scores = excerpt.scores.order_by(Score.wpm.desc()).all()

    # only 3 top scores
    top_scores = []

    for x in range(3 if len(scores) > 3 else len(scores)):
      top_scores.append({
        'id': scores[x].id,
        'value': scores[x].wpm
      })
    
    return jsonify({
      'excerpt': {
        'id': excerpt.id,
        'text': excerpt.text,
        'scores': {
          'top_scores': top_scores,
          'scores_count': scores_count
        }
      }
    }), 200
