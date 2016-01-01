from app import app
import os

if __name__ == '__main__':
    port = os.getenv('PORT', 8080)
    app.run(debug=True, host='0.0.0.0', port=port)
