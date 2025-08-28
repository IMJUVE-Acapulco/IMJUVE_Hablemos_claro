from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv

def create_app():
    load_dotenv()

    app = Flask(__name__)

    # Configuración de MongoDB
    username = quote_plus(os.getenv('MONGO_USER', 'Roberto'))
    password = quote_plus(os.getenv('MONGO_PASS', '12345'))
    MONGO_URI = f"mongodb+srv://{username}:{password}@cluster0.vkow89i.mongodb.net/conferencia_joven?retryWrites=true&w=majority&authSource=admin"
    DB_NAME = "conferencia_joven"

    # Conexión a MongoDB
    try:
        client = MongoClient(
            MONGO_URI,
            connectTimeoutMS=5000,
            serverSelectionTimeoutMS=5000
        )
        client.admin.command('ping')
        db = client[DB_NAME]
        pages_collection = db['pages']
        feedback_collection = db['feedback']
        print("✅ Conexión exitosa a MongoDB Atlas")
    except Exception as e:
        print(f"❌ Error de conexión a MongoDB: {str(e)}")
        pages_collection = None
        feedback_collection = None

    @app.route('/')
    def index():
        if pages_collection is not None:  # CORREGIDO: usar is not None
            pages = list(pages_collection.find({}))
        else:
            pages = []
        return render_template('index.html', pages=pages)

    @app.route('/admin')
    def admin():
        if pages_collection is not None:  # CORREGIDO: usar is not None
            pages = list(pages_collection.find({}))
        else:
            pages = []
        return render_template('admin.html', pages=pages)

    @app.route('/page/<page_id>')
    def show_page(page_id):
        if pages_collection is not None:  # CORREGIDO: usar is not None
            try:
                page = pages_collection.find_one({'_id': ObjectId(page_id)})
                if page:
                    return render_template('page.html', page=page)
            except:
                pass
        return "Página no encontrada", 404

    @app.route('/add_page', methods=['POST'])
    def add_page():
        if pages_collection is None:  # CORREGIDO: usar is None
            return jsonify({'success': False, 'error': 'Error de base de datos'})
        
        title = request.form.get('title')
        content = request.form.get('content')
        speaker = request.form.get('speaker')
        logo_type = request.form.get('logo_type', 'imjuve')
        
        if not title or not content:
            return jsonify({'success': False, 'error': 'Faltan campos obligatorios'})
        
        page_data = {
            'title': title,
            'content': content,
            'speaker': speaker if speaker else '',
            'logo_type': logo_type,
            'filename': f"{title.lower().replace(' ', '_')}.html"
        }
        
        result = pages_collection.insert_one(page_data)
        return jsonify({'success': True, 'page_id': str(result.inserted_id)})

    @app.route('/edit_page/<page_id>', methods=['GET', 'POST'])
    def edit_page(page_id):
        if pages_collection is None:  # CORREGIDO: usar is None
            return "Error de base de datos", 500
        
        if request.method == 'GET':
            try:
                page = pages_collection.find_one({'_id': ObjectId(page_id)})
                if page:
                    return render_template('edit_page.html', page=page)
            except:
                pass
            return "Página no encontrada", 404
        
        # POST request - actualizar página
        title = request.form.get('title')
        content = request.form.get('content')
        speaker = request.form.get('speaker')
        logo_type = request.form.get('logo_type', 'imjuve')
        
        if not title or not content:
            return jsonify({'success': False, 'error': 'Faltan campos obligatorios'})
        
        try:
            pages_collection.update_one(
                {'_id': ObjectId(page_id)},
                {'$set': {
                    'title': title,
                    'content': content,
                    'speaker': speaker if speaker else '',
                    'logo_type': logo_type,
                    'filename': f"{title.lower().replace(' ', '_')}.html"
                }}
            )
            return jsonify({'success': True})
        except:
            return jsonify({'success': False, 'error': 'Error al actualizar'})

    @app.route('/delete_page/<page_id>', methods=['POST'])
    def delete_page(page_id):
        if pages_collection is not None:  # CORREGIDO: usar is not None
            try:
                pages_collection.delete_one({'_id': ObjectId(page_id)})
                return jsonify({'success': True})
            except:
                return jsonify({'success': False, 'error': 'Error al eliminar'})
        return jsonify({'success': False, 'error': 'Error de base de datos'})

    @app.route('/submit-feedback', methods=['POST'])
    def submit_feedback():
        if feedback_collection is None:  # CORREGIDO: usar is None
            return jsonify({'success': False, 'error': 'Error de base de datos'})
        
        data = request.get_json()
        feedback_collection.insert_one(data)
        return jsonify({'success': True})
    
    return app  # Retornar la aplicación

# Crear la aplicación
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)