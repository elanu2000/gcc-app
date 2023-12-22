from flask import Flask, request, jsonify
from flask_cors import CORS
import update_total_score  # Your backend logic

app = Flask(__name__)
CORS(app)

@app.route('/process_match', methods=['POST'])
def process_match():
    print("hey")
    match = request.json.get('match')
    # Call your backend function here with `match`
    # result = update_total_score.run_total_score(match)
    # result = "hey"
    result = jsonify({'result': match})
    # result.headers.add('Access-Control-Allow-Origin', '*')
    print(result)
    return result

if __name__ == '__main__':
    app.run(debug=True)
