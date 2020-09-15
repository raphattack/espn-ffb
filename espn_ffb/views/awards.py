from flask import Blueprint, render_template

awards = Blueprint("awards", __name__, template_folder="templates")


@awards.route('/awards/<int:year>', methods=['GET'])
def show(year: int):
    return render_template(f"awards/{year}.html", title=f'{year} Awards')
