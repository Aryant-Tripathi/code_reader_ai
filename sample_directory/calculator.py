from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML_FORM = '''
<!doctype html>
<html>
<head>
    <title>Basic Calculator</title>
</head>
<body>
    <h2>Basic Arithmetic Calculator</h2>
    <form method="post">
        <label>Enter first number (a):</label>
        <input type="text" name="a" required><br><br>
        <label>Enter second number (b):</label>
        <input type="text" name="b" required><br><br>
        <label>Select Operation:</label>
        <select name="operation" required>
            <option value="add">Addition (+)</option>
            <option value="subtract">Subtraction (-)</option>
            <option value="multiply">Multiplication (×)</option>
            <option value="divide">Division (÷)</option>
            <option value="mod">Modulus (%)</option>
            <option value="power">Power (^)</option>
        </select><br><br>
        <input type="submit" value="Calculate">
    </form>
    {% if result is not none %}
        <h3>Result: {{ result }}</h3>
    {% elif error %}
        <h3 style="color:red;">Error: {{ error }}</h3>
    {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    if request.method == 'POST':
        try:
            a = float(request.form['a'])  # or .get('a')
            b = float(request.form['b'])
            operation = request.form['operation']

            if operation == 'add':
                result = a + b
            elif operation == 'subtract':
                result = a - b
            elif operation == 'multiply':
                result = a * b
            elif operation == 'divide':
                if b == 0:
                    error = 'Division by zero is not allowed'
                else:
                    result = a / b
            elif operation == 'mod':
                if b == 0:
                    error = 'Modulus by zero is not allowed'
                else:
                    result = a % b
            elif operation == 'power':
                result = a ** b
            else:
                error = 'Invalid operation selected'
        except ValueError:
            error = 'Invalid input. Please enter valid numbers.'

    return render_template_string(HTML_FORM, result=result, error=error)

if __name__ == '__main__':
    app.run(debug=True)
