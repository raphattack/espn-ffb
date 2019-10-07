from flask import Blueprint, render_template

awards = Blueprint("awards", __name__, template_folder="templates")


@awards.route('/awards', methods=['GET'])
def show():
    return render_template("awards.html", title='Settings')
