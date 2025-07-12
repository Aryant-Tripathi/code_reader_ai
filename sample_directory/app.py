from flask import Flask, request, jsonify, abort

app = Flask(__name__)

# In-memory 'database'
items = []
next_id = 1

# Create a new item
@app.route('/items', methods=['POST'])
def create_item():
    global next_id
    data = request.get_json()

    if not data or 'name' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    item = {
        'id': next_id,
        'name': data['name']
    }
    items.append(item)
    next_id += 1
    return jsonify(item), 201

# Get all items
@app.route('/items', methods=['GET'])
def get_items():
    return jsonify(items)

# Get a single item by ID
@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = next((i for i in items if i['id'] == item_id), None)
    if item is None:
        abort(404, description="Item not found")
    return jsonify(item)

# Update an item
@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.get_json()
    item = next((i for i in items if i['id'] == item_id), None)
    if item is None:
        abort(404, description="Item not found")
    if not data or 'name' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    item['name'] = data['name']
    return jsonify(item)

# Delete an item
@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    global items
    item = next((i for i in items if i['id'] == item_id), None)
    if item is None:
        abort(404, description="Item not found")

    items = [i for i in items if i['id'] != item_id]
    return jsonify({'message': f'Item {item_id} deleted successfully'})

# Run the app
if __name__ == '__main__':
    app.run(debug=False)
