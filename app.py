from flask import Flask, render_template, request, redirect, url_for, send_file, session
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
from functools import wraps

# Import modules
from modules.health_score import calculate_health_score
from modules.outlier_detector import detect_outliers
from modules.pdf_report_generator import generate_pdf_report

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')

# Config
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['REPORTS_FOLDER'] = 'reports'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['LAST_REPORT'] = None  # Store last analyzed report
app.config['LAST_FILENAME'] = None  # Store last uploaded filename

# Password protection config
REQUIRED_PASSWORD = "AIREPORT2026"

# Create folders
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)


# =========================
# Password Protection Decorator
# =========================

def login_required(f):
    """Decorator to protect routes that require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def analyze_dataset(df):
    """Complete dataset analysis returning comprehensive report"""
    report = {}

    # =========================
    # Dataset Summary
    # =========================

    total_rows = len(df)
    total_cols = len(df.columns)
    duplicate_rows = int(df.duplicated().sum())

    mem_usage_kb = df.memory_usage(deep=True).sum() / 1024

    if mem_usage_kb > 1024:
        mem_usage = f"{round(mem_usage_kb / 1024, 1)} MB"
    else:
        mem_usage = f"{round(mem_usage_kb, 1)} KB"
    
    mem_usage_raw = round(mem_usage_kb, 1)

    report["Dataset Summary"] = {
        "Total Rows": int(total_rows),
        "Total Columns": int(total_cols),
        "Duplicate Rows": int(duplicate_rows),
        "Memory Usage": mem_usage,
        "Memory Usage Raw KB": mem_usage_raw
    }

    # =========================
    # Missing Values
    # =========================

    missing_dict = {}
    total_missing = 0

    for col in df.columns:
        missing_count = int(df[col].isna().sum())
        missing_percent = round((missing_count / total_rows) * 100, 1) if total_rows > 0 else 0
        missing_dict[col] = {
            "count": missing_count,
            "percent": missing_percent
        }
        total_missing += missing_count

    report["Missing Values"] = missing_dict
    report["Total Missing Values"] = total_missing
    report["Overall Missing Percent"] = round((total_missing / (total_rows * total_cols)) * 100, 1) if total_rows * total_cols > 0 else 0

    # =========================
    # Data Types
    # =========================

    dtype_dict = {}
    for col in df.columns:
        dtype_dict[col] = str(df[col].dtype)

    report["Data Types"] = dtype_dict

    # =========================
    # Column Analysis
    # =========================

    column_analysis = {}
    for col in df.columns:
        column_analysis[col] = {
            "datatype": str(df[col].dtype),
            "missing": int(df[col].isna().sum()),
            "missing_percent": round((int(df[col].isna().sum()) / total_rows) * 100, 1) if total_rows > 0 else 0,
            "unique": int(df[col].nunique()),
            "unique_percent": round((int(df[col].nunique()) / total_rows) * 100, 1) if total_rows > 0 else 0
        }

    report["Column Analysis"] = column_analysis

    # =========================
    # Numeric Statistics
    # =========================

    numeric_stats = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) > 0:
            numeric_stats[col] = {
                "mean": round(float(series.mean()), 2),
                "median": round(float(series.median()), 2),
                "std": round(float(series.std()), 2),
                "min": round(float(series.min()), 2),
                "max": round(float(series.max()), 2),
                "q1": round(float(series.quantile(0.25)), 2),
                "q3": round(float(series.quantile(0.75)), 2)
            }

    report["Numeric Statistics"] = numeric_stats

    # =========================
    # Outlier Detection
    # =========================

    outliers_result = detect_outliers(df)

    outliers_data = {
        "outliers_found": False,
        "total_outliers": 0,
        "columns_with_outliers": [],
        "outliers_detail": {},
        "outlier_percentage": 0
    }

    if isinstance(outliers_result, dict):
        for col_name, col_data in outliers_result.items():
            if isinstance(col_data, dict):
                outlier_count = int(col_data.get('count', col_data.get('outliers', 0)))
            elif isinstance(col_data, (int, float)):
                outlier_count = int(col_data)
            else:
                outlier_count = 0

            if outlier_count > 0:
                outliers_data["outliers_found"] = True
                outliers_data["columns_with_outliers"].append(col_name)
                outliers_data["total_outliers"] += outlier_count

            outliers_data["outliers_detail"][col_name] = {
                "outlier_count": int(outlier_count),
                "outlier_percentage": round((outlier_count / total_rows) * 100, 1) if total_rows > 0 else 0
            }

    if total_rows > 0:
        outliers_data["outlier_percentage"] = round((outliers_data["total_outliers"] / total_rows) * 100, 1)

    report["Outliers"] = outliers_data

    # =========================
    # Health Score
    # =========================

    health_result = calculate_health_score(df, outliers_data)

    if isinstance(health_result, dict):
        report["Health Score"] = {
            "overall_score": float(health_result.get('overall_score', health_result.get('score', 0))),
            "completeness": float(health_result.get('completeness', 0)),
            "quality_score": float(health_result.get('quality_score', 0))
        }
    elif isinstance(health_result, (int, float)):
        report["Health Score"] = {
            "overall_score": round(float(health_result), 1),
            "completeness": round(float(health_result), 1),
            "quality_score": round(float(health_result), 1)
        }
    else:
        report["Health Score"] = {
            "overall_score": 75,
            "completeness": 75,
            "quality_score": 75
        }

    # =========================
    # Column Names
    # =========================
    report["Column Names"] = list(df.columns)
    report["Total Numeric Columns"] = len(numeric_cols)
    report["Total Categorical Columns"] = total_cols - len(numeric_cols)
    report["Generated At"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return report


# =========================
# Error Handler
# =========================

@app.errorhandler(413)
def too_large(e):
    return render_template('error.html', message="File too large! Maximum file size is 50MB"), 413


# =========================
# Login / Password Protection Routes
# =========================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Password entry page"""
    # If already authenticated, redirect to home
    if session.get('authenticated'):
        return redirect(url_for('index'))
    
    error = None
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        
        if password == REQUIRED_PASSWORD:
            session['authenticated'] = True
            session.permanent = True  # Session persists across browser sessions
            return redirect(url_for('index'))
        else:
            error = "Incorrect password. Please try again."
    
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('login'))


# =========================
# Home Page (Protected)
# =========================

@app.route('/')
@login_required
def index():
    return render_template('index.html')


# =========================
# Upload Route (Protected)
# =========================

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        return redirect(url_for('index'))

    if file and file.filename.endswith('.csv'):
        # File size check
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        max_size = 50 * 1024 * 1024

        if file_size > max_size:
            return render_template('error.html', message="File size exceeds 50MB")

        # Generate unique filename to prevent conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)

        file.save(filepath)

        try:
            df = pd.read_csv(filepath)
            report = analyze_dataset(df)
            
            # Store report and filename in Flask config (backend memory)
            app.config['LAST_REPORT'] = report
            app.config['LAST_FILENAME'] = file.filename
            
            # Also store in session for user-specific storage (optional)
            session['last_report'] = report
            session['last_filename'] = file.filename

            return render_template('report.html', report=report, filename=file.filename)

        except Exception as e:
            return render_template('error.html', message=str(e))

    return redirect(url_for('index'))


# =========================
# PDF Download Route (Protected)
# =========================

@app.route('/download-pdf', methods=['POST', 'GET'])
@login_required
def download_pdf():
    """Generate and download professional PDF report using stored backend data"""
    try:
        # Retrieve report from backend memory
        report = app.config.get('LAST_REPORT')
        filename = app.config.get('LAST_FILENAME')
        
        # Fallback to session if config is empty
        if not report:
            report = session.get('last_report')
            filename = session.get('last_filename')
        
        if not report:
            return render_template('error.html', message="No report data available. Please upload a CSV file first."), 400
        
        # Generate PDF
        pdf_filename, pdf_path = generate_pdf_report(report, filename)
        
        if pdf_path and os.path.exists(pdf_path):
            return send_file(
                pdf_path,
                as_attachment=True,
                download_name=pdf_filename,
                mimetype='application/pdf'
            )
        else:
            return render_template('error.html', message="Failed to generate PDF report"), 500
            
    except Exception as e:
        print(f"PDF Generation Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template('error.html', message=f"Error generating PDF: {str(e)}"), 500


# =========================
# Cleanup Old Files Route (Optional, Protected)
# =========================

@app.route('/cleanup', methods=['POST'])
@login_required
def cleanup():
    """Clean up old files from uploads and reports folders"""
    try:
        import time
        current_time = time.time()
        # Delete files older than 1 hour
        deleted_count = 0
        for folder in [app.config['UPLOAD_FOLDER'], app.config['REPORTS_FOLDER']]:
            for filename in os.listdir(folder):
                filepath = os.path.join(folder, filename)
                if os.path.isfile(filepath):
                    file_age = current_time - os.path.getctime(filepath)
                    if file_age > 3600:  # 1 hour
                        os.remove(filepath)
                        deleted_count += 1
        return {"status": "success", "message": f"Cleanup completed. Deleted {deleted_count} files."}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500


# =========================
# Run App
# =========================

if __name__ == '__main__':
    app.run(debug=True)  