import io
from datetime import datetime
import pandas as pd
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_csv(records: list) -> bytes:
    df = pd.DataFrame(records)
    if df.empty:
        df = pd.DataFrame(columns=['EPC', 'ReaderName', 'Location', 'Antenna', 'RSSI', 'Timestamp', 'CreatedAt'])
    else:
        column_mapping = {
            'epc': 'EPC',
            'reader_name': 'ReaderName',
            'location': 'Location',
            'antenna': 'Antenna',
            'rssi': 'RSSI',
            'timestamp': 'Timestamp',
            'created_at': 'CreatedAt'
        }
        df = df[[col for col in column_mapping.keys() if col in df.columns]]
        df = df.rename(columns=column_mapping)
        # Format timestamps nicely for CSV
        for col in ['Timestamp', 'CreatedAt']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')
        desired_cols = ['EPC', 'ReaderName', 'Location', 'Antenna', 'RSSI', 'Timestamp', 'CreatedAt']
        df = df.reindex(columns=desired_cols)
        
    output = io.StringIO()
    df.to_csv(output, index=False)
    return output.getvalue().encode('utf-8')

def generate_excel(records: list) -> bytes:
    df = pd.DataFrame(records)
    if df.empty:
        df = pd.DataFrame(columns=['EPC', 'ReaderName', 'Location', 'Antenna', 'RSSI', 'Timestamp', 'CreatedAt'])
    else:
        column_mapping = {
            'epc': 'EPC',
            'reader_name': 'ReaderName',
            'location': 'Location',
            'antenna': 'Antenna',
            'rssi': 'RSSI',
            'timestamp': 'Timestamp',
            'created_at': 'CreatedAt'
        }
        df = df[[col for col in column_mapping.keys() if col in df.columns]]
        df = df.rename(columns=column_mapping)
        for col in ['Timestamp', 'CreatedAt']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')
        desired_cols = ['EPC', 'ReaderName', 'Location', 'Antenna', 'RSSI', 'Timestamp', 'CreatedAt']
        df = df.reindex(columns=desired_cols)
        
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Tag Reads')
    return output.getvalue()

def generate_pdf(records: list) -> bytes:
    output = io.BytesIO()
    
    # Landscape orientation fits all table columns nicely
    doc = SimpleDocTemplate(
        output,
        pagesize=landscape(letter),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        name='TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1E3A8A'),
        alignment=0,
        spaceAfter=15
    )
    
    header_style = ParagraphStyle(
        name='HeaderStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        fontName='Helvetica-Bold',
        textColor=colors.white
    )
    
    cell_style = ParagraphStyle(
        name='CellStyle',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        fontName='Helvetica'
    )
    
    cell_mono_style = ParagraphStyle(
        name='CellMonoStyle',
        parent=styles['Normal'],
        fontSize=7,
        leading=9,
        fontName='Courier'
    )

    story = []
    
    story.append(Paragraph("Tag Reads Report", title_style))
    
    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    meta_style = ParagraphStyle(
        name='MetaStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#6B7280'),
        spaceAfter=15
    )
    story.append(Paragraph(f"Generated at: {current_time_str} | Total Records: {len(records)}", meta_style))
    story.append(Spacer(1, 10))
    
    headers = ['EPC', 'Reader', 'Location', 'Antenna', 'RSSI', 'Timestamp', 'Created At']
    data = []
    data.append([Paragraph(h, header_style) for h in headers])
    
    for r in records:
        epc = r.get('epc', '')
        reader_name = r.get('reader_name', '')
        location = r.get('location', '') or ''
        antenna = str(r.get('antenna', ''))
        rssi = str(r.get('rssi', ''))
        
        ts = r.get('timestamp')
        if ts:
            if isinstance(ts, datetime):
                ts_str = ts.strftime('%Y-%m-%d %H:%M:%S')
            else:
                try:
                    ts_str = datetime.fromisoformat(str(ts).replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    ts_str = str(ts)
        else:
            ts_str = ''
            
        ca = r.get('created_at')
        if ca:
            if isinstance(ca, datetime):
                ca_str = ca.strftime('%Y-%m-%d %H:%M:%S')
            else:
                try:
                    ca_str = datetime.fromisoformat(str(ca).replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    ca_str = str(ca)
        else:
            ca_str = ''
            
        data.append([
            Paragraph(epc, cell_mono_style),
            Paragraph(reader_name, cell_style),
            Paragraph(location, cell_style),
            Paragraph(antenna, cell_style),
            Paragraph(rssi, cell_style),
            Paragraph(ts_str, cell_style),
            Paragraph(ca_str, cell_style)
        ])
    
    col_widths = [200, 120, 100, 50, 50, 106, 106]
    
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
    ]))
    
    story.append(t)
    doc.build(story)
    
    return output.getvalue()
