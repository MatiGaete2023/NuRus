"""Exportación de tablas del trabajo actual."""
from pathlib import Path
from nurus.services.file_output import write_new_file

def _book(sheets, destination):
    from openpyxl import Workbook
    from openpyxl.styles import Border, Side, PatternFill, Font, Alignment
    from openpyxl.utils import get_column_letter
    book=Workbook();book.remove(book.active)
    edge=Side(style='thin',color='000000')
    try:
        for name,headers,rows in sheets:
            sheet=book.create_sheet(name);sheet.append(headers)
            for row in rows:
                sheet.append(row)
                for cell in sheet[sheet.max_row]:
                    if isinstance(cell.value,str):cell.data_type='s'
            for cells in sheet:
                for cell in cells:
                    cell.border=Border(left=edge,right=edge,top=edge,bottom=edge)
                    cell.alignment=Alignment(vertical='top',wrap_text=True)
            for cell in sheet[1]:
                cell.fill=PatternFill('solid',fgColor='1F538D');cell.font=Font(color='FFFFFF',bold=True)
            for number,title in enumerate(headers,1):
                sheet.column_dimensions[get_column_letter(number)].width=60 if title in ('Texto','Detalle','Trámite') else 25
            sheet.freeze_panes='A2';sheet.auto_filter.ref=sheet.dimensions
        write_new_file(destination,book.save)
    finally:book.close()
    return str(Path(destination))
