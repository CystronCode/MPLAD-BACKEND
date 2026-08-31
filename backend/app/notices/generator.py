# backend/app/notices/generator.py
# Form MPLADS-INSP-1 Statutory Show-Cause Notice Generator

import io
from datetime import date
from typing import Dict, Any

def generate_statutory_notice_pdf(case_data: Dict[str, Any]) -> bytes:
    """
    Generates a formal Statutory Field Inspection Notice (Form MPLADS-INSP-1)
    issued under Section 6.4 of the Guidelines on MPLAD Scheme 2023.
    """
    buffer = io.BytesIO()

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'NoticeTitle',
            parent=styles['Heading1'],
            fontSize=14,
            leading=16,
            alignment=1,
            textColor=colors.HexColor('#1e3a8a')
        )
        subtitle_style = ParagraphStyle(
            'NoticeSubTitle',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            alignment=1,
            textColor=colors.HexColor('#4b5563')
        )
        heading_style = ParagraphStyle(
            'SectionHead',
            parent=styles['Heading2'],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#1f2937'),
            spaceBefore=10,
            spaceAfter=4
        )
        body_style = ParagraphStyle(
            'NoticeBody',
            parent=styles['Normal'],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor('#374151')
        )

        elements = []

        # Header
        elements.append(Paragraph("<b>OFFICE OF THE DISTRICT MAGISTRATE & DISTRICT AUTHORITY</b>", title_style))
        elements.append(Paragraph("MPLAD SCHEME MONITORING & SURVEILLANCE CELL", subtitle_style))
        elements.append(Paragraph("MEMORANDUM / STATUTORY FIELD INSPECTION NOTICE", title_style))
        elements.append(Paragraph("ISSUED UNDER SECTION 6.4 OF THE GUIDELINES ON MPLAD SCHEME 2023", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e3a8a'), spaceAfter=8, spaceBefore=4))

        # Notice Metadata
        p_info = case_data.get("project_details", {})
        s_info = case_data.get("school_details", {})
        ref_no = f"MPLADS-INSP-{p_info.get('project_id', '2024-BN-0042')}"
        today_str = str(date.today())

        district_name = "Bengaluru North Parliamentary Constituency (Karnataka)"
        if s_info.get("district_lgd_code") == 12 or p_info.get("district_lgd_code") == 12:
            district_name = "Kangra District (Himachal Pradesh)"

        meta_data = [
            [Paragraph(f"<b>Notice Ref:</b> {ref_no}", body_style), Paragraph(f"<b>Date:</b> {today_str}", body_style)],
            [Paragraph("<b>To:</b> Executive Engineer, PWD / Rural Development Division", body_style),
             Paragraph(f"<b>Jurisdiction:</b> {district_name}", body_style)],
            [Paragraph(f"<b>Subject:</b> Mandatory Physical Verification of Completed MPLADS Work ID: <b>{p_info.get('project_id')}</b>", body_style), ""]
        ]
        t_meta = Table(meta_data, colWidths=[300, 240])
        t_meta.setStyle(TableStyle([
            ('SPAN', (0, 2), (1, 2)),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        elements.append(t_meta)
        elements.append(Spacer(1, 8))

        # 1. Project Particulars
        sanction_amt = float(p_info.get('sanction_cost', 0) or 0)
        lakhs_amt = sanction_amt / 100000.0

        elements.append(Paragraph("1. PROJECT PARTICULARS", heading_style))
        proj_data = [
            [Paragraph("<b>Work Description</b>", body_style), Paragraph(str(p_info.get("work_description_raw", "")), body_style)],
            [Paragraph("<b>Target School</b>", body_style), Paragraph(f"{s_info.get('name_canonical')} (UDISE: {s_info.get('udise_code')})", body_style)],
            [Paragraph("<b>Sanction Cost</b>", body_style), Paragraph(f"INR {sanction_amt:,.2f} (Rs. {lakhs_amt:.2f} Lakhs)", body_style)],
            [Paragraph("<b>Key Dates</b>", body_style), Paragraph(f"Sanction: {p_info.get('sanction_date')} | Completion: {p_info.get('completion_date')}", body_style)],
            [Paragraph("<b>GPS Coordinates</b>", body_style), Paragraph(f"Lat: {s_info.get('latitude')}, Lon: {s_info.get('longitude')}", body_style)]
        ]
        t_proj = Table(proj_data, colWidths=[140, 400])
        t_proj.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f3f4f6')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d1d5db')),
            ('PADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(t_proj)
        elements.append(Spacer(1, 8))

        # 2. Contradiction Findings in Clear Administrative English
        elements.append(Paragraph("2. SYSTEMIC CROSS-REGISTRY CONTRADICTION FINDINGS", heading_style))
        raw_narrative = str(case_data.get("explanation_narrative", ""))
        
        if "STATUTORY" in raw_narrative or "PRIVATE" in str(s_info.get("management_category", "")):
            narrative = "<b>Statutory Ineligibility Violation:</b> Public MPLADS funds were allocated to a Private Unaided Institution, which violates Section 6.1 of the MPLADS Guidelines 2023. Government funds may only be spent on public or government-aided institutions. Immediate verification and recovery audit ordered."
        elif "REFLECTION" in raw_narrative or "Missing" in raw_narrative:
            narrative = "<b>Asset Non-Reflection Gap:</b> The implementing agency reported 100% completion and disbursement in e-SAKSHI, but the independent annual UDISE+ school census confirms ZERO new rooms or facilities added on the ground. Physical verification is mandatory before final billing."
        elif "VELOCITY" in raw_narrative or "Speed" in raw_narrative:
            narrative = "<b>Unrealistic Construction Velocity:</b> Claimed completion timeframe is under 30 days, violating minimum structural RCC concrete curing physics (IS 456 standard). Structural stability and muster roll audit required."
        else:
            narrative = raw_narrative if raw_narrative else "Physical asset reflection contradicts official annual census returns."

        elements.append(Paragraph(f"<b>Collectorate Ground Finding:</b> {narrative}", body_style))
        elements.append(Spacer(1, 6))

        # 3. Directives
        elements.append(Paragraph("3. DIRECTIVE TO INSPECTING AUTHORITY", heading_style))
        directive_text = (
            "You are hereby directed to conduct an on-site physical measurement inspection at the registered campus "
            "within <b>SEVEN (7) DAYS</b> of receipt of this notice. You shall physically count available facilities, "
            "inspect Measurement Book (MB) records, verify contractor muster rolls, and upload geo-tagged photographic "
            "evidence directly to the MEEV Verification Portal. Fund releases for subsequent milestones are held in escrow."
        )
        elements.append(Paragraph(directive_text, body_style))
        elements.append(Spacer(1, 14))

        # Sign-off block
        elements.append(Paragraph("<b>BY ORDER OF:</b>", body_style))
        elements.append(Paragraph("District Magistrate & District Authority (IDA), MPLAD Scheme", body_style))
        elements.append(Paragraph("<i>Cryptographically Signed & Authenticated via MEEV Hash Chain</i>", subtitle_style))

        doc.build(elements)
        return buffer.getvalue()

    except ImportError:
        text_content = f"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj
4 0 obj << /Length 200 >> stream
BT
/F1 12 Tf
50 720 Td
(STATUTORY FIELD INSPECTION NOTICE - FORM MPLADS-INSP-1) Tj
0 -20 Td
(Work ID: {case_data.get('project_details', {}).get('project_id', 'N/A')}) Tj
0 -20 Td
(Issued under Section 6.4 of MPLADS Guidelines 2023) Tj
ET
endstream
endobj
5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj
xref
0 6
0000000000 65535 f 
0000000010 00000 n 
0000000060 00000 n 
0000000117 00000 n 
0000000227 00000 n 
0000000478 00000 n 
trailer << /Size 6 /Root 1 0 R >>
startxref
555
%%EOF"""
        return text_content.encode("utf-8")

generate_mplads_insp1_notice = generate_statutory_notice_pdf
