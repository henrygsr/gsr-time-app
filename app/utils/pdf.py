from flask import render_template
from xhtml2pdf import pisa
from io import BytesIO

def render_pdf_from_template(template_name, **context):
    html = render_template(template_name, **context)
    result = BytesIO()
    pisa.CreatePDF(html, dest=result)
    result.seek(0)
    return result.read()
