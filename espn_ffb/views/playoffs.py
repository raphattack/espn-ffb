from flask import Blueprint, render_template

playoffs = Blueprint("playoffs", __name__, template_folder="templates")


@playoffs.route('/playoffs/<int:year>', methods=['GET'])
def show(year):
    # noinspection PyUnresolvedReferences
    return render_template(f"playoffs/{year}.html", title='{year} Playoffs')
