from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, KeepInFrame, NextPageTemplate, BaseDocTemplate, Frame, PageTemplate
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

class DynamicDocTemplate(BaseDocTemplate):
    """Custom document template with dynamic page management"""
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        # Create a single page template that will be used for all pages
        frame = Frame(
            self.leftMargin, 
            self.bottomMargin, 
            self.width, 
            self.height,
            id='normal',
            showBoundary=0
        )
        self.addPageTemplates([
            PageTemplate(id='All', frames=[frame], onPage=self.header_footer)
        ])
    
    def header_footer(self, canvas, doc):
        """Header and footer for all pages"""
        canvas.saveState()
        
        # Header
        canvas.setFillColor(colors.HexColor('#1E3A8A'))
        canvas.rect(0, doc.height + doc.topMargin - 25, doc.width + doc.leftMargin + doc.rightMargin, 60, fill=1, stroke=0)
        
        canvas.setFillColor(colors.HexColor('#FFFFFF'))
        canvas.setFont('Helvetica-Bold', 14)
        canvas.drawString(doc.leftMargin, doc.height + doc.topMargin - 5, "AI Dataset Analytics Report")
        
        canvas.setFont('Helvetica', 8)
        canvas.drawRightString(doc.width + doc.leftMargin, doc.height + doc.topMargin - 5, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Footer
        canvas.setFillColor(colors.HexColor('#F3F4F6'))
        canvas.rect(0, doc.bottomMargin - 40, doc.width + doc.leftMargin + doc.rightMargin, 40, fill=1, stroke=0)
        
        canvas.setFillColor(colors.HexColor('#6B7280'))
        canvas.setFont('Helvetica', 8)
        canvas.drawCentredString(doc.width/2 + doc.leftMargin, doc.bottomMargin - 22, f"Page {doc.page} • Confidential Report")
        
        canvas.restoreState()


class PDFReportGenerator:
    def __init__(self):
        # Create reports directory if not exists
        if not os.path.exists('reports'):
            os.makedirs('reports')
        
        # Color palette
        self.colors = {
            'primary': colors.HexColor('#1E3A8A'),
            'secondary': colors.HexColor('#3B82F6'),
            'accent': colors.HexColor('#10B981'),
            'warning': colors.HexColor('#F59E0B'),
            'danger': colors.HexColor('#EF4444'),
            'info': colors.HexColor('#8B5CF6'),
            'gray': colors.HexColor('#6B7280'),
            'light_gray': colors.HexColor('#F3F4F6'),
            'white': colors.HexColor('#FFFFFF'),
            'dark': colors.HexColor('#111827'),
            'success': colors.HexColor('#059669'),
            'border': colors.HexColor('#E5E7EB')
        }
        
        # Page dimensions
        self.page_width = A4[0]
        self.page_height = A4[1]
        self.left_margin = 40
        self.right_margin = 40
        self.top_margin = 80
        self.bottom_margin = 80
        self.available_width = self.page_width - self.left_margin - self.right_margin
        
    def create_title_section(self, filename):
        """Create title page"""
        elements = []
        
        # Large top spacer
        elements.append(Spacer(1, 120))
        
        # Main Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=getSampleStyleSheet()['Title'],
            fontSize=36,
            textColor=self.colors['primary'],
            alignment=TA_CENTER,
            spaceAfter=25,
            fontName='Helvetica-Bold'
        )
        
        elements.append(Paragraph("DATA QUALITY REPORT", title_style))
        elements.append(Spacer(1, 15))
        
        # Subtitle
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=getSampleStyleSheet()['Normal'],
            fontSize=14,
            textColor=self.colors['gray'],
            alignment=TA_CENTER,
            spaceAfter=50,
            fontName='Helvetica'
        )
        
        elements.append(Paragraph("Comprehensive Dataset Profiling & Analytics", subtitle_style))
        
        # Decorative line
        drawing = Drawing(400, 3)
        drawing.add(Rect(0, 0, 400, 3, fillColor=self.colors['secondary'], strokeColor=None))
        elements.append(drawing)
        elements.append(Spacer(1, 60))
        
        # Clean dataset name
        clean_filename = filename.replace('_report_', '').replace('.pdf', '')
        if '_' in clean_filename and len(clean_filename) > 30:
            parts = clean_filename.split('_')
            if len(parts) > 2 and parts[-1].isdigit():
                clean_filename = '_'.join(parts[:-1])
        
        # Info box
        info_drawing = Drawing(450, 120)
        info_drawing.add(Rect(0, 0, 450, 120, fillColor=self.colors['light_gray'], strokeColor=self.colors['border'], rx=10, ry=10))
        
        info_drawing.add(String(225, 80, f"Dataset: {clean_filename}", fontSize=12, fillColor=self.colors['primary'], textAnchor='middle', fontName='Helvetica-Bold'))
        info_drawing.add(String(225, 55, f"Analysis Date: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}", fontSize=10, fillColor=self.colors['gray'], textAnchor='middle', fontName='Helvetica'))
        info_drawing.add(String(225, 32, f"Report ID: {datetime.now().strftime('%Y%m%d%H%M%S')}", fontSize=9, fillColor=self.colors['gray'], textAnchor='middle', fontName='Helvetica'))
        
        elements.append(info_drawing)
        elements.append(Spacer(1, 80))
        
        return elements
    
    def create_metric_card(self, label, value, color, width=200):
        """Create a metric card"""
        drawing = Drawing(width, 85)
        
        # Card background
        drawing.add(Rect(0, 0, width, 85, fillColor=self.colors['white'], strokeColor=self.colors['border'], strokeWidth=1, rx=8, ry=8))
        
        # Value
        drawing.add(String(width/2, 52, str(value), fontSize=28, fillColor=color, textAnchor='middle', fontName='Helvetica-Bold'))
        
        # Label
        drawing.add(String(width/2, 25, label, fontSize=10, fillColor=self.colors['gray'], textAnchor='middle', fontName='Helvetica'))
        
        return drawing
    
    def create_overview_section(self, report):
        """Create dataset overview with metrics"""
        elements = []
        
        # Section header
        header_style = ParagraphStyle(
            'SectionHeader',
            parent=getSampleStyleSheet()['Heading2'],
            fontSize=18,
            textColor=self.colors['primary'],
            spaceAfter=15,
            fontName='Helvetica-Bold'
        )
        
        elements.append(Paragraph("📋 Dataset Overview", header_style))
        elements.append(Spacer(1, 10))
        
        # Extract metrics
        dataset_summary = report.get("Dataset Summary", {})
        health_score = report.get("Health Score", {})
        
        metrics = [
            ("Total Rows", f"{dataset_summary.get('Total Rows', 0):,}", self.colors['primary']),
            ("Total Columns", f"{dataset_summary.get('Total Columns', 0)}", self.colors['secondary']),
            ("Duplicate Rows", f"{dataset_summary.get('Duplicate Rows', 0):,}", self.colors['warning'] if dataset_summary.get('Duplicate Rows', 0) > 0 else self.colors['success']),
            ("Memory Usage", dataset_summary.get('Memory Usage', 'N/A'), self.colors['gray']),
            ("Health Score", f"{health_score.get('overall_score', 0)}%", self.colors['accent']),
            ("Total Missing", f"{report.get('Total Missing Values', 0):,}", self.colors['danger'] if report.get('Total Missing Values', 0) > 0 else self.colors['success'])
        ]
        
        # Create metrics in rows of 3
        for i in range(0, len(metrics), 3):
            row_metrics = []
            for j in range(3):
                if i + j < len(metrics):
                    label, value, color = metrics[i + j]
                    row_metrics.append(self.create_metric_card(label, value, color, 180))
                else:
                    row_metrics.append(Spacer(10, 1))
            
            metric_table = Table([row_metrics], colWidths=[190, 190, 190])
            metric_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, -1), self.colors['white']),
            ]))
            elements.append(metric_table)
            elements.append(Spacer(1, 12))
        
        return elements
    
    def create_health_score_section(self, report):
        """Create health score section"""
        elements = []
        
        header_style = ParagraphStyle(
            'SectionHeader',
            parent=getSampleStyleSheet()['Heading2'],
            fontSize=18,
            textColor=self.colors['primary'],
            spaceAfter=15,
            fontName='Helvetica-Bold'
        )
        
        elements.append(Paragraph("🏥 Data Health Score Analysis", header_style))
        elements.append(Spacer(1, 10))
        
        health_score = report.get("Health Score", {})
        
        # Health score gauge
        gauge_drawing = Drawing(400, 130)
        gauge_drawing.add(Rect(100, 15, 200, 105, fillColor=self.colors['light_gray'], strokeColor=self.colors['border'], rx=10, ry=10))
        
        score_value = health_score.get('overall_score', 0)
        
        if score_value >= 80:
            score_color = self.colors['success']
        elif score_value >= 60:
            score_color = self.colors['warning']
        else:
            score_color = self.colors['danger']
        
        gauge_drawing.add(String(200, 75, f"{score_value}%", fontSize=38, fillColor=score_color, textAnchor='middle', fontName='Helvetica-Bold'))
        gauge_drawing.add(String(200, 42, "Overall Quality Score", fontSize=10, fillColor=self.colors['gray'], textAnchor='middle', fontName='Helvetica'))
        
        elements.append(gauge_drawing)
        elements.append(Spacer(1, 20))
        
        # Sub-scores
        completeness = health_score.get('completeness', 0)
        quality = health_score.get('quality_score', 0)
        
        sub_scores_data = [
            ['Metric', 'Score', 'Status'],
            ['Completeness', f"{completeness}%", '✓ Good' if completeness > 70 else '⚠️ Needs Attention'],
            ['Quality Score', f"{quality}%", '✓ Good' if quality > 70 else '⚠️ Needs Attention']
        ]
        
        sub_table = Table(sub_scores_data, colWidths=[180, 100, 180])
        sub_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['white']),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), self.colors['white']),
            ('GRID', (0, 0), (-1, -1), 0.5, self.colors['border']),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.colors['white'], self.colors['light_gray']]),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(KeepTogether(sub_table))
        
        return elements
    
    def create_missing_values_table(self, report):
        """Create missing values table"""
        elements = []
        
        header_style = ParagraphStyle(
            'SectionHeader',
            parent=getSampleStyleSheet()['Heading2'],
            fontSize=16,
            textColor=self.colors['primary'],
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        elements.append(Paragraph("🔍 Missing Values Analysis", header_style))
        elements.append(Spacer(1, 10))
        
        missing_values = report.get("Missing Values", {})
        
        missing_data = []
        for col, miss_info in missing_values.items():
            if miss_info.get('count', 0) > 0:
                missing_data.append([col, miss_info.get('count', 0), f"{miss_info.get('percent', 0)}%"])
        
        missing_data.sort(key=lambda x: x[1], reverse=True)
        
        # Summary
        summary_text = f"Total Missing Values: {report.get('Total Missing Values', 0):,} | Overall Missing: {report.get('Overall Missing Percent', 0)}%"
        summary_style = ParagraphStyle(
            'Summary',
            parent=getSampleStyleSheet()['Normal'],
            fontSize=10,
            textColor=self.colors['gray'],
            alignment=TA_LEFT,
            spaceAfter=12
        )
        elements.append(Paragraph(summary_text, summary_style))
        
        if missing_data:
            table_data = [['Column Name', 'Missing Count', 'Missing %']] + missing_data[:15]
            
            table = Table(table_data, colWidths=[280, 100, 80])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['white']),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (2, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), self.colors['white']),
                ('TEXTCOLOR', (0, 1), (-1, -1), self.colors['dark']),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, self.colors['border']),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.colors['white'], self.colors['light_gray']]),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            elements.append(KeepTogether(table))
        else:
            no_missing_style = ParagraphStyle(
                'NoMissing',
                parent=getSampleStyleSheet()['Normal'],
                fontSize=11,
                textColor=self.colors['success'],
                alignment=TA_CENTER,
                spaceBefore=20,
                spaceAfter=20
            )
            elements.append(Paragraph("✓ No missing values found in this dataset!", no_missing_style))
        
        return elements
    
    def create_data_types_table(self, report):
        """Create data types table"""
        elements = []
        
        header_style = ParagraphStyle(
            'SectionHeader',
            parent=getSampleStyleSheet()['Heading2'],
            fontSize=16,
            textColor=self.colors['primary'],
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        elements.append(Paragraph("📊 Column Data Types", header_style))
        elements.append(Spacer(1, 10))
        
        data_types = report.get("Data Types", {})
        
        dtype_counts = {}
        for dtype in data_types.values():
            dtype_counts[dtype] = dtype_counts.get(dtype, 0) + 1
        
        dtype_data = [[str(dtype), count, f"{(count/len(data_types))*100:.1f}%"] 
                     for dtype, count in dtype_counts.items()]
        
        if dtype_data:
            table_data = [['Data Type', 'Count', 'Percentage']] + dtype_data
            
            table = Table(table_data, colWidths=[280, 100, 80])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['secondary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['white']),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (2, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), self.colors['white']),
                ('GRID', (0, 0), (-1, -1), 0.5, self.colors['border']),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.colors['white'], self.colors['light_gray']]),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            elements.append(KeepTogether(table))
        
        return elements
    
    def create_column_analysis_table(self, report):
        """Create column analysis table"""
        elements = []
        
        header_style = ParagraphStyle(
            'SectionHeader',
            parent=getSampleStyleSheet()['Heading2'],
            fontSize=16,
            textColor=self.colors['primary'],
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        elements.append(Paragraph("📝 Column-wise Analysis", header_style))
        elements.append(Spacer(1, 10))
        
        column_analysis = report.get("Column Analysis", {})
        
        col_data = []
        for col, details in column_analysis.items():
            col_data.append([
                col[:35] + '...' if len(col) > 35 else col, 
                details.get('datatype', 'N/A'), 
                details.get('missing', 0),
                details.get('unique', 0),
                f"{details.get('missing_percent', 0)}%"
            ])
        
        if col_data:
            # Show all columns, let platypus handle pagination automatically
            table_data = [['Column Name', 'Data Type', 'Missing', 'Unique', 'Missing %']] + col_data
            
            table = Table(table_data, colWidths=[140, 90, 60, 60, 70], repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['accent']),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['white']),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (4, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BACKGROUND', (0, 1), (-1, -1), self.colors['white']),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, self.colors['border']),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.colors['white'], self.colors['light_gray']]),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            elements.append(table)
            
            # Add note if many columns
            if len(col_data) > 25:
                note_style = ParagraphStyle(
                    'Note',
                    parent=getSampleStyleSheet()['Normal'],
                    fontSize=8,
                    textColor=self.colors['gray'],
                    alignment=TA_LEFT,
                    spaceBefore=8
                )
                elements.append(Paragraph(f"Note: Showing all {len(col_data)} columns", note_style))
        
        return elements
    
    def create_numeric_statistics(self, report):
        """Create numeric statistics table"""
        elements = []
        
        header_style = ParagraphStyle(
            'SectionHeader',
            parent=getSampleStyleSheet()['Heading2'],
            fontSize=16,
            textColor=self.colors['primary'],
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        elements.append(Paragraph("📈 Numeric Columns Statistics", header_style))
        elements.append(Spacer(1, 10))
        
        numeric_stats = report.get("Numeric Statistics", {})
        
        if numeric_stats:
            stats_data = [['Column', 'Mean', 'Median', 'Min', 'Max', 'Std Dev']]
            
            for col, stats in numeric_stats.items():
                stats_data.append([
                    col[:25] + '...' if len(col) > 25 else col,
                    f"{stats.get('mean', 0):.2f}",
                    f"{stats.get('median', 0):.2f}",
                    f"{stats.get('min', 0):.2f}",
                    f"{stats.get('max', 0):.2f}",
                    f"{stats.get('std', 0):.2f}"
                ])
            
            table = Table(stats_data, colWidths=[100, 70, 70, 60, 60, 70], repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['info']),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['white']),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BACKGROUND', (0, 1), (-1, -1), self.colors['white']),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, self.colors['border']),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.colors['white'], self.colors['light_gray']]),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            elements.append(table)
            
            summary_style = ParagraphStyle(
                'Summary',
                parent=getSampleStyleSheet()['Normal'],
                fontSize=9,
                textColor=self.colors['gray'],
                alignment=TA_LEFT,
                spaceBefore=10
            )
            elements.append(Paragraph(f"Total numeric columns analyzed: {len(numeric_stats)}", summary_style))
        else:
            elements.append(Paragraph("No numeric columns found in dataset for statistical analysis", 
                                     getSampleStyleSheet()['Normal']))
        
        return elements
    
    def create_outlier_analysis(self, report):
        """Create outlier analysis table"""
        elements = []
        
        header_style = ParagraphStyle(
            'SectionHeader',
            parent=getSampleStyleSheet()['Heading2'],
            fontSize=16,
            textColor=self.colors['primary'],
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        elements.append(Paragraph("⚠️ Outlier Detection Analysis", header_style))
        elements.append(Spacer(1, 10))
        
        outliers = report.get("Outliers", {})
        outliers_detail = outliers.get('outliers_detail', {})
        
        if outliers_detail:
            outlier_data = [['Column', 'Outlier Count', 'Outlier %', 'Status']]
            
            has_outliers = False
            for col, details in outliers_detail.items():
                outlier_count = details.get('outlier_count', 0)
                outlier_pct = details.get('outlier_percentage', 0)
                
                if outlier_count > 0:
                    has_outliers = True
                    status = "⚠️ Has Outliers"
                else:
                    status = "✓ No Outliers"
                
                outlier_data.append([
                    col[:30] + '...' if len(col) > 30 else col,
                    outlier_count,
                    f"{outlier_pct:.1f}%",
                    status
                ])
            
            # Sort by outlier count
            if len(outlier_data) > 1:
                outlier_data[1:] = sorted(outlier_data[1:], key=lambda x: x[1], reverse=True)
            
            table = Table(outlier_data, colWidths=[160, 80, 80, 140], repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['warning']),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['white']),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (2, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), self.colors['white']),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, self.colors['border']),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.colors['white'], self.colors['light_gray']]),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            elements.append(table)
            
            # Summary and recommendations
            total_outliers = outliers.get('total_outliers', 0)
            cols_with_outliers = outliers.get('columns_with_outliers', [])
            outlier_percentage = outliers.get('outlier_percentage', 0)
            
            if has_outliers and total_outliers > 0:
                summary_style = ParagraphStyle(
                    'Summary',
                    parent=getSampleStyleSheet()['Normal'],
                    fontSize=10,
                    textColor=self.colors['danger'],
                    alignment=TA_LEFT,
                    spaceBefore=12,
                    spaceAfter=5
                )
                
                elements.append(Paragraph(f"⚠️ Detected {total_outliers:,} total outliers across {len(cols_with_outliers)} columns ({outlier_percentage}% of total rows).", summary_style))
                
                recommendation_style = ParagraphStyle(
                    'Recommendation',
                    parent=getSampleStyleSheet()['Normal'],
                    fontSize=9,
                    textColor=self.colors['gray'],
                    alignment=TA_LEFT,
                    spaceBefore=5
                )
                elements.append(Paragraph("💡 <b>Recommendation:</b> Consider handling outliers through statistical methods (capping, transformation, winsorization) or domain-based rules for improved model performance.", recommendation_style))
            else:
                clean_style = ParagraphStyle(
                    'Clean',
                    parent=getSampleStyleSheet()['Normal'],
                    fontSize=11,
                    textColor=self.colors['success'],
                    alignment=TA_CENTER,
                    spaceBefore=20,
                    spaceAfter=20
                )
                elements.append(Paragraph("✓ No outliers detected in numeric columns. Data quality is excellent!", clean_style))
        else:
            elements.append(Paragraph("No outlier analysis data available. This may occur if there are no numeric columns in the dataset.", 
                                     getSampleStyleSheet()['Normal']))
        
        return elements
    
    def generate_report(self, report, filename="dataset_report.pdf"):
        """Generate complete PDF report with proper pagination"""
        
        # Use custom document template for better page management
        doc = DynamicDocTemplate(
            f"reports/{filename}",
            pagesize=A4,
            leftMargin=self.left_margin,
            rightMargin=self.right_margin,
            topMargin=self.top_margin,
            bottomMargin=self.bottom_margin
        )
        
        # Build story with page breaks between major sections
        story = []
        
        # Title section (Page 1)
        story.extend(self.create_title_section(filename))
        story.append(PageBreak())
        
        # Dataset Overview + Health Score (Page 2)
        story.extend(self.create_overview_section(report))
        story.append(Spacer(1, 20))
        story.extend(self.create_health_score_section(report))
        story.append(PageBreak())
        
        # Missing Values + Data Types (Page 3)
        story.extend(self.create_missing_values_table(report))
        story.append(Spacer(1, 20))
        story.extend(self.create_data_types_table(report))
        story.append(PageBreak())
        
        # Column Analysis (Pages 4+)
        story.extend(self.create_column_analysis_table(report))
        story.append(PageBreak())
        
        # Numeric Statistics (Next page)
        story.extend(self.create_numeric_statistics(report))
        story.append(Spacer(1, 20))
        
        # Outlier Analysis (Same page or next)
        story.extend(self.create_outlier_analysis(report))
        
        # Final footer note
        footer_style = ParagraphStyle(
            'FooterNote',
            parent=getSampleStyleSheet()['Normal'],
            fontSize=8,
            textColor=self.colors['gray'],
            alignment=TA_CENTER,
            spaceBefore=30,
            spaceAfter=20
        )
        story.append(Spacer(1, 30))
        story.append(Paragraph("Report generated automatically by AI Dataset Analytics System • Data is for internal use only", footer_style))
        
        # Build PDF
        doc.build(story)
        
        return f"reports/{filename}"


# Flask integration function
def generate_pdf_report(report, filename):
    """
    Main function to be called from Flask routes
    
    Args:
        report: Dictionary containing complete dataset analysis report
        filename: Original CSV filename (used for PDF naming)
    
    Returns:
        tuple: (pdf_filename, pdf_path)
    """
    try:
        generator = PDFReportGenerator()
        
        # Generate PDF filename
        if filename:
            base_name = os.path.splitext(filename)[0]
            pdf_filename = f"{base_name}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        else:
            pdf_filename = f"dataset_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Generate the PDF
        pdf_path = generator.generate_report(report, pdf_filename)
        
        return pdf_filename, pdf_path
        
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        raise 