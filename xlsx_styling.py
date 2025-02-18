import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

def apply_styles(file_name): 
    wb = openpyxl.load_workbook(file_name)
    ws = wb.active
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="0073CF", end_color="0073CF", fill_type="solid")
    border_style = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"))
    for col in range(1, ws.max_column + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border_style
    column_widths = [71, 29, 13, 8, 11]
    for i, width in enumerate(column_widths, start=1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = width
    for row in ws.iter_rows():
        for cell in row:
            cell.border = border_style
    wb.save(file_name)