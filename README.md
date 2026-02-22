# Text Comparison Web App (Final Project - Data Structures)

This is a Django-based web application for advanced **text comparison and similarity analysis**, developed as a final project for a Data Structures course. The application supports Persian language text comparison using various algorithms including Levenshtein distance.

## 🔍 Features

- 🔠 **Standard Text Comparison** (using edit distance/Levenshtein algorithm)
- 🔊 **Phonetic Comparison** (similar sounding words in Persian)
- 📊 **Graph-Based Visualization** of edit operations
- 💡 **Highlighted Differences** in words and sounds
- 🧠 **Multiple Algorithm Modes**: `standard`, `phonetic`, `persian`
- 🌐 **Web UI** for input and comparison
- 📄 **Markdown Report Generation** for comparison results
- 🇮🇷 **Full Persian Language Support** with proper preprocessing

## 🚀 Technologies Used

- **Django 4.2+** (Backend Framework)
- **Python 3.8+** (Core logic and algorithms)
- **jdatetime** (Persian date/time support)
- **HTML/CSS** (Frontend templates)
- **JavaScript** (for UI enhancement and graph visualization)
- **D3.js** (for interactive graph visualization)

## 📦 Installation

1. Clone the repository (replace with your repository URL):
   ```bash
   git clone <repository-url>
   cd textdiff
   ```
   
   Or if you already have the project files, navigate to the project directory:
   ```bash
   cd textdiff
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # Edit .env file and set your SECRET_KEY
   # You can generate a secret key using:
   python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   ```
   
   **Important:** The `SECRET_KEY` is required for the application to run. Make sure to set it in your `.env` file.

5. Run database migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser (optional, for admin access):
   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```bash
   python manage.py runserver
   ```

8. Open your browser and navigate to `http://127.0.0.1:8000/`

## 📖 Usage

### Web Interface

1. Navigate to the home page at `http://127.0.0.1:8000/`
2. Enter two texts in the input fields
3. Click "Compare" to see the comparison results
4. View detailed analysis including:
   - Character-by-character comparison
   - Word-by-word alignment
   - Similarity percentage
   - Operation details (match, substitute, insert, delete)
5. Download comparison report as Markdown file

### API Endpoints

#### Compare Texts (POST)
```bash
POST /api/compare/
Content-Type: application/x-www-form-urlencoded

text1=سلام&text2=سلام
```

**Response:**
```json
{
    "text1": "سلام",
    "text2": "سلام",
    "highlighted_text1": "...",
    "highlighted_text2": "...",
    "total_cost": 0,
    "operations": [...],
    "similarity": 100.0
}
```

#### Get Graph Data (GET)
```bash
GET /api/graph-data/?text1=سلام&text2=سلام&mode=standard
```

**Response:**
```json
{
    "nodes": [...],
    "edges": [...],
    "metadata": {
        "text1": "سلام",
        "text2": "سلام",
        "type": "word_comparison",
        "operations_count": 4,
        "stats": {...}
    }
}
```

## 🏗️ Project Structure

```
textdiff/
├── textdiff/              # Django project settings
│   ├── settings.py        # Project settings
│   ├── urls.py          # URL configuration
│   └── wsgi.py          # WSGI configuration
├── comparator/           # Main application
│   ├── algorithms/      # Core algorithms
│   │   ├── comparator.py      # Text comparison logic
│   │   ├── preprocessing.py    # Text preprocessing
│   │   ├── alignment.py        # Text alignment
│   │   ├── highlighting.py     # Difference highlighting
│   │   └── report.py           # Report generation
│   ├── views.py         # View functions
│   ├── urls.py          # URL routing
│   └── models.py        # Database models
├── requestlog/          # Request logging app
├── templates/           # HTML templates
├── static/              # Static files (CSS, JS)
├── reports/             # Generated reports
├── requirements.txt     # Python dependencies
└── manage.py            # Django management script
```

## ⚙️ Configuration

### Environment Variables

You can configure the application using environment variables. Create a `.env` file in the project root (see `env.example` for a template):

- `SECRET_KEY`: Django secret key (**required** - application will not start without it)
- `DEBUG`: Enable/disable debug mode (default: True)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `MAX_TEXT_LENGTH`: Maximum text length (default: 10000)
- `MAX_WORDS`: Maximum word count (default: 2000)
- `GRAPHVIZ_PATH`: Path to Graphviz binaries (optional, mainly for Windows)

**Example `.env` file:**
```bash
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
MAX_TEXT_LENGTH=10000
MAX_WORDS=2000
GRAPHVIZ_PATH=C:\Program Files\Graphviz\bin
```

**Note:** The application uses `python-dotenv` to load environment variables from the `.env` file automatically.

## 🧪 Testing

Run tests using Django's test framework:

```bash
python manage.py test
```

## 📝 API Documentation

### Comparison Modes

- **standard**: Standard Levenshtein distance comparison
- **phonetic**: Phonetic comparison (similar sounding words)
- **persian**: Persian-specific text normalization and comparison

### Limitations

- Maximum text length: 10,000 characters (configurable)
- Maximum word count: 2,000 words (configurable)
- Currently optimized for Persian language

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is developed as a final project for a Data Structures course.

## 👥 Authors

- Developed as part of Data Structures course project

## 🙏 Acknowledgments

- Django framework
- Levenshtein distance algorithm
- Persian text processing libraries
