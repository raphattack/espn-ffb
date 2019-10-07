from collections import namedtuple
from flask import Blueprint, current_app, render_template

champions = Blueprint("champions", __name__, template_folder="templates")
TABLE_HEADERS = ['Year', 'Champion']
COLUMN_NAMES = ['year', 'champion']
Record = namedtuple('Champions', COLUMN_NAMES)


def get_records(query):
    records = list()
    champions, owners = zip(*query.get_champions())

    for c, o in zip(champions, owners):
        records.append(Record(year=c.year, champion=o.first_name + " " + o.last_name))

    return records


@champions.route('/champions', methods=['GET'])
def show():
    query = current_app.config.get("QUERY")
    records = get_records(query)

    return render_template('champions.html', title='Champions', table_headers=TABLE_HEADERS,
                           column_names=COLUMN_NAMES, records=records)
