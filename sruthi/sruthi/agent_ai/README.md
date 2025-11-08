
# AI-Powered Answer Grading System

This application uses Google's Gemini AI to automatically grade student answers from PDF submissions. It provides detailed feedback and grades for each submission.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Internet connection
- Web browser (Chrome, Firefox, or Edge recommended)

### Installation

1. **Clone or download** this repository
2. **Navigate** to the project directory in your terminal
3. **Set up a virtual environment** (recommended):
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Mac/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install google-generativeai
   ```

5. **Set up environment variables**:
   Create a `.env` file in the project root with:
   ```
   GEMINI_API_KEY=AIzaSyCna0ATJwFqlzklMihEhM-XRqhcLQoMXZs
   FLASK_SECRET=your-secret-key-here
   ```

### 🏃‍♂️ Running the Application

1. **Start the Flask server**:
   ```bash
   # Windows
   set FLASK_APP=app.py
   set FLASK_DEBUG=1
   flask run

   # Mac/Linux
   export FLASK_APP=app.py
   export FLASK_DEBUG=1
   flask run
   ```

2. **Access the application** in your browser:
   ```
   http://127.0.0.1:5000
   ```

## 🎯 Features

- **PDF Upload**: Upload answer sheets in PDF format
- **AI-Powered Grading**: Uses Google's Gemini AI for accurate grading
- **Detailed Feedback**: Provides comprehensive feedback for each answer
- **Export Results**: Download graded results as CSV
- **Simple Interface**: Easy-to-use web interface

## 📁 Project Structure

```
.
├── app.py              # Main application code
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create this)
├── uploads/           # Stores uploaded PDFs (created automatically)
└── templates/         # HTML templates
    └── index.html     # Main web interface
```

## 🔧 Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   # Find and kill the process using port 5000
   # Windows
   netstat -ano | findstr :5000
   taskkill /PID <PID> /F
   
   # Mac/Linux
   lsof -i :5000
   kill -9 <PID>
   ```

2. **Dependency issues**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

3. **API key issues**:
   - Ensure the `.env` file exists and contains the correct API key
   - Verify the key has the correct permissions

## 📝 Notes

- The application is configured to use a test API key. For production use, replace it with your own Gemini API key.
- All uploaded files are stored locally in the `uploads` directory.
- The application is meant for educational purposes and should be used responsibly.

## PDF Format

For best results, format your PDF with answers like this:
```
RegNo: 123
Section: A
Answer: The mitochondria is the powerhouse of the cell.

RegNo: 124
Section: B
Answer: Photosynthesis occurs in the chloroplasts of plant cells.
```

## 🤝 Contributing

Feel free to submit issues and enhancement requests.

## 📄 License

This project is licensed under the MIT License.
