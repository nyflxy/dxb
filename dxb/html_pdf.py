# -*- coding:utf-8 -*-

import pdfkit

def html_to_pdf(html_file,pdf_file):
        path_wkthmltopdf = r'C:\Python27\wkhtmltopdf\bin\wkhtmltopdf.exe'#先安装wkhtmltox-0.12.3.2_msvc2013-win64，path_wkthtmltopdf为其安装路径
        config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
        pdfkit.from_url(html_file, pdf_file, configuration=config)
