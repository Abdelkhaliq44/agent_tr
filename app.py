# from flask import Flask, request, jsonify
# from main import run_ai

# app = Flask(__name__)
# @app.route('/route', methods=['POST'])
# def get_route():
#     try:
#         data = request.get_json()
#         required_fields = ['lat1', 'long1', 'lat2', 'long2', 'document']
#         for field in required_fields:
#             if  field not in data :
#                 return jsonify({"error": f"Missing field: {field}"}), 400
#         inputs = {
#             'lat1': data['lat1'],
#             'long1': data['long1'],
#             'lat2': data['lat2'],
#             'long2': data['long2'],
#             'document': data['document'],
#         }

#         result = run_ai(inputs)
#         return jsonify({
#             "data": result
#         })
    
#     except Exception as e:
#         return jsonify({
#             "status": "error",
#             "message": str(e)
#         }), 500
# if __name__ == '__main__':
#        app.run(host="0.0.0.0", port=5000, debug=True)
from flask import Flask, request, jsonify
from main import run_ai
from selector import run_selector
import traceback

app = Flask(__name__)


@app.route('/route', methods=['POST'])
def get_route():
    try:
        data = request.get_json()
        required_fields = ['lat1', 'long1', 'lat2', 'long2', 'document']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        inputs = {
            'lat1':     data['lat1'],
            'long1':    data['long1'],
            'lat2':     data['lat2'],
            'long2':    data['long2'],
            'document': data['document'],
        }

        result = run_ai(inputs)
        return jsonify({"data": result})

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.route('/select-lines', methods=['POST'])
def select_lines():
    try:
        data = request.get_json()
        required = ['lat1', 'long1', 'lat2', 'long2', 'Cost', 'time', 'Comfort']
        for f in required:
            if f not in data:
                return jsonify({"error": f"Missing field: {f}"}), 400

        result = run_selector({
            'lat1':    data['lat1'],
            'long1':   data['long1'],
            'lat2':    data['lat2'],
            'long2':   data['long2'],
            'Cost':    data['Cost'],
            'time':    data['time'],
            'Comfort': data['Comfort'],
        })
        return jsonify({"data": result})

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)