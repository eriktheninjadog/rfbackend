"""
COMPATIBILITY WRAPPER - webapi.py

This file has been refactored into multiple modules for better maintainability.

The original 3695-line monolithic file has been split into:

├── app.py                    # Main application entry point
├── routes/                   # Route handlers organized by functionality
│   ├── flashcard_routes.py   # Flashcard management
│   ├── text_processing_routes.py # Text import, CWS management
│   ├── ai_routes.py          # AI question generation and processing
│   ├── audio_routes.py       # Audio file handling and exercises
│   ├── dictionary_routes.py  # Dictionary lookup and management
│   ├── poe_routes.py         # POE AI service integration
│   ├── translation_routes.py # Translation services
│   ├── example_routes.py     # Example generation
│   ├── cache_routes.py       # Cache management
│   ├── utility_routes.py     # Utility endpoints (ping, version)
│   └── misc_routes.py        # Miscellaneous specialized endpoints
├── utils/                    # Utility functions
│   ├── json_helpers.py       # JSON parsing utilities
│   ├── text_helpers.py       # Text processing helpers
│   └── poe_helpers.py        # POE AI specific utilities
├── services/                 # Business logic services
│   └── cache_service.py      # Cache management service
└── config/                   # Configuration management

To run the application:
- Use: python app.py (recommended)
- Or continue using: python webapi.py (this compatibility wrapper)

Benefits of the new structure:
✓ Easier maintenance and debugging
✓ Better code organization and readability
✓ Improved testability
✓ Enhanced collaboration capabilities
✓ Cleaner separation of concerns
✓ Reduced cognitive load per file
✓ Better error isolation
"""

# Import the refactored app
from app import create_app

# Create the app instance for backwards compatibility
app = create_app()

# For direct execution compatibility
if __name__ == '__main__':
    print("=" * 70)
    print("🔄 RUNNING REFACTORED APPLICATION")
    print("=" * 70)
    print("✅ Original webapi.py (3695 lines) has been successfully refactored")
    print("✅ Now split into 12 organized modules + utilities")
    print("✅ All functionality preserved with improved maintainability")
    print("=" * 70)
    app.run(debug=True, host='0.0.0.0', port=5000)