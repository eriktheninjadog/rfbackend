"""Main Flask application file - refactored from webapi.py"""
from flask import Flask

# Import all blueprint modules
from routes import (
    flashcard_routes,
    text_processing_routes,
    ai_routes,
    audio_routes,
    dictionary_routes,
    poe_routes,
    translation_routes,
    example_routes,
    cache_routes,
    utility_routes,
    misc_routes,
    session_routes,
    study_routes,
    queue_routes,
    game_routes,
    dmapi_routes
)


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Register all blueprints
    app.register_blueprint(flashcard_routes.bp)
    app.register_blueprint(text_processing_routes.bp)
    app.register_blueprint(ai_routes.bp)
    app.register_blueprint(audio_routes.bp)
    app.register_blueprint(dictionary_routes.bp)
    app.register_blueprint(poe_routes.bp)
    app.register_blueprint(translation_routes.bp)
    app.register_blueprint(example_routes.bp)
    app.register_blueprint(cache_routes.bp)
    app.register_blueprint(utility_routes.bp)
    app.register_blueprint(misc_routes.bp)
    app.register_blueprint(session_routes.bp)
    app.register_blueprint(study_routes.bp)
    app.register_blueprint(queue_routes.bp)
    app.register_blueprint(game_routes.bp)
    app.register_blueprint(dmapi_routes.bp)
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)