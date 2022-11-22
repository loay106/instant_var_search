import atexit

from flask import Flask, request, abort, jsonify

from ds_manager import DSVARManager

app = Flask(__name__)
ds_client = DSVARManager('INSERT-PROJECT-NAME-HERE')
ds_client.begin()


@app.route("/set", methods=['POST'])
def set_var():
    params = request.args.to_dict()
    if {'name', 'value'} != set(params):
        abort(400)
    name = params['name']
    value = params['value']
    result = ds_client.set_var(name, value)
    return jsonify(result)


@app.route("/get", methods=['GET'])
def get_var():
    params = request.args.to_dict()
    if {'name'} != set(params):
        abort(400)
    name = params['name']
    result = ds_client.get_var(name)
    return jsonify(result)


@app.route("/unset", methods=['PUT'])
def unset_var():
    params = request.args.to_dict()
    if {'name'} != set(params):
        abort(400)
    name = params['name']
    result = ds_client.unset_var(name)
    return jsonify(result)


@app.route("/numequalto", methods=['GET'])
def get_value_count():
    params = request.args.to_dict()
    if {'value'} != set(params):
        abort(400)
    value = params['value']
    result = ds_client.get_value_count(value)
    return jsonify(result)


@app.route("/undo", methods=['POST'])
def undo():
    params = request.args.to_dict()
    if len(params) != 0:
        abort(400)
    result = ds_client.undo()
    return jsonify(result)


@app.route("/redo", methods=['POST'])
def redo():
    params = request.args.to_dict()
    if len(params) != 0:
        abort(400)
    result = ds_client.redo()
    return jsonify(result)


@app.route("/clean", methods=['DELETE'])
def clean_all():
    params = request.args.to_dict()
    if len(params) != 0:
        abort(400)
    ds_client.clean()


def __exit_handler():
    ds_client.end()


atexit.register(__exit_handler)
