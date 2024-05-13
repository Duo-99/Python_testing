from odoo import models, fields, api, _
import base64
import io

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

DATE_DICT = {
    '%m/%d/%Y': 'mm/dd/yyyy',
    '%Y/%m/%d': 'yyyy/mm/dd',
    '%m/%d/%y': 'mm/dd/yy',
    '%d/%m/%Y': 'dd/mm/yyyy',
    '%d/%m/%y': 'dd/mm/yy',
    '%d-%m-%Y': 'dd-mm-yyyy',
    '%d-%m-%y': 'dd-mm-yy',
    '%m-%d-%Y': 'mm-dd-yyyy',
    '%m-%d-%y': 'mm-dd-yy',
    '%Y-%m-%d': 'yyyy-mm-dd',
    '%f/%e/%Y': 'm/d/yyyy',
    '%f/%e/%y': 'm/d/yy',
    '%e/%f/%Y': 'd/m/yyyy',
    '%e/%f/%y': 'd/m/yy',
    '%f-%e-%Y': 'm-d-yyyy',
    '%f-%e-%y': 'm-d-yy',
    '%e-%f-%Y': 'd-m-yyyy',
    '%e-%f-%y': 'd-m-yy'
}

class PartnerLedger(models.TransientModel):
    _inherit = "ins.partner.ageing"

    def print_partner_xlsx(self):
        data = self.read()[0]
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        lang = self.env.user.lang
        lang_id = self.env['res.lang'].search([('code', '=', lang)])[0]

        record = self.env['ins.partner.ageing'].browse(data.get('id', [])) or False
        filter, ageing_lines, period_dict, period_list = record.get_report_datas()

        data = self.get_filters()
        as_on_date = fields.Date.from_string(str(data['as_on_date'])).strftime('%d %b %Y')

        sheet_num = 0


        if record.include_details:
            if ageing_lines:
                for line in ageing_lines:
                    if line != 'Total':
                        count, offset, sub_lines, period_list = record.process_detailed_data(partner=line,
                                                                                             fetch_range=1000000)
                        partner = self.env['res.partner'].browse(line)
                        customer_code = partner['code']
                        partner_name = partner['name']

                        sheet_num += 1

                        if customer_code:
                            sheet = workbook.add_worksheet(f"{customer_code}")
                        else:
                            sheet = workbook.add_worksheet(f"{sheet_num}_{partner_name}")

                        sheet.set_zoom(100)

                        sheet.set_column(0, 0, 17.86)
                        sheet.set_column('B:B', 15.57)
                        sheet.set_column('C:C', 14.29)
                        sheet.set_column('D:D', 11.43)
                        sheet.set_column('E:E', 24.29)

                        format_title = workbook.add_format({
                            'bold': True,
                            'font_size': 11,
                            'underline': True
                        })

                        format_header = workbook.add_format({
                            'bold': True,
                            'font_size': 11,
                        })

                        table_border = workbook.add_format({
                            'border': 1,
                        })

                        table_header = workbook.add_format({
                            'bold': True,
                            'border': 1,
                            "fg_color": "#b6c5de",
                            'align': 'center',
                            'font_size': 8,
                        })

                        normal_bold = workbook.add_format({
                            'bold': True
                        })

                        up_border = workbook.add_format({'top': 1, })

                        bottom_border = workbook.add_format({'bottom': 1, })
                        right_border = workbook.add_format({'right': 1, })
                        right_bottom = workbook.add_format({
                            'right': 1,
                            'bottom': 1,
                        })
                        right_bottom_up = workbook.add_format({
                            'right': 1,
                            'bottom': 1,
                            'top': 1,
                        })

                        if partner['street']:
                            address = partner['street']
                        else:
                            address = ''

                        if partner['phone']:
                            phone = partner['phone']
                        else:
                            phone = ''

                        sheet.write(0, 0, '')
                        sheet.write(1, 0, '')
                        sheet.write(2, 0, '')
                        sheet.write(3, 0, 'Dear Sir/Mdm,')
                        sheet.write(4, 0, '')
                        sheet.write(5, 0, 'Audit Confirmation', format_title)
                        sheet.write(6, 0,
                                    'Our record show that the balance of your account with us is as follows: -')
                        sheet.write(7, 0, '')
                        sheet.write(8, 0, f"BALANCE AS AT {as_on_date} DUE FROM YOU", format_header)
                        sheet.write(9, 0, '')
                        sheet.write(10, 0, 'Name                    :', format_header)
                        sheet.write(11, 0, 'Township              :', format_header)
                        sheet.write(12, 0, 'Address                :', format_header)
                        sheet.write(13, 0, 'Phone No.             :', format_header)

                        sheet.write(10, 1, f"{partner_name}", format_header)
                        sheet.write(12, 1, f"{address}", format_header)
                        sheet.write(13, 1, f"{phone}", format_header)

                        sheet.write(14, 0, 'Date', table_header)
                        sheet.write(14, 1, 'Invoice No', table_header)
                        sheet.write(14, 2, 'Amount(MMK)', table_header)
                        sheet.write(14, 3, 'Amount(USD)', table_header)
                        sheet.write(14, 4, 'Remark', table_header)

                        sheet.write(10, 1, f"{partner_name}", format_header)
                        sheet.write(12, 1, f"{address}", format_header)
                        sheet.write(13, 1, f"{phone}", format_header)

                        count_inv = 0
                        sum_inv_amount = 0
                        row_pos = 14

                        for sub_line in sub_lines:

                            account_move = self.env['account.move'].browse(sub_line.get('move_id'))




                            inv_amount = account_move['amount_total_signed']

                            row_pos += 1

                            datestring = fields.Date.from_string(
                                str(sub_line.get('date_maturity') or sub_line.get('date'))).strftime(
                                lang_id.date_format)
                            sheet.write(row_pos, 0, datestring, table_border)
                            sheet.write(row_pos, 1, sub_line.get('move_name') or '', table_border)
                            sheet.write(row_pos, 2, float(inv_amount), table_border)
                            sheet.write(row_pos, 3, '', table_border)
                            sheet.write(row_pos, 4, '', table_border)

                            count_inv += 1
                            sum_inv_amount += inv_amount
                            count_inv += 1

                            row_pos += 1
                            sheet.write(row_pos, 0, 'Total Balance', table_border)

                            row_pos += 1
                            sheet.write(row_pos, 0, 'Total Balance', table_border)

                            if sum_inv_amount !=0:
                                sheet.write(row_pos, 1, '', table_border)
                                sheet.write(row_pos, 2, sum_inv_amount, table_border)
                                sheet.write(row_pos, 3, '', table_border)
                                sheet.write(row_pos, 4, '', table_border)
                            else:
                                sheet.write(row_pos, 1, '', table_border)
                                sheet.write(row_pos, 2, '', table_border)
                                sheet.write(row_pos, 4, '', table_border)

                        if sum_inv_amount != 0:
                            sheet.write(row_pos, 1, '', table_border)
                            sheet.write(row_pos, 2, sum_inv_amount, table_border)
                            sheet.write(row_pos, 3, '', table_border)
                            sheet.write(row_pos, 4, '', table_border)
                        else:
                            sheet.write(row_pos, 1, '', table_border)
                            sheet.write(row_pos, 2, '', table_border)
                            sheet.write(row_pos, 4, '', table_border)

                        row_pos += 1
                        sheet.write(row_pos, 0, 'Total Number of Receive', table_border)

                        if count_inv != 0:
                            sheet.write(row_pos, 1, '', table_border)
                            sheet.write(row_pos, 2, '', table_border)
                            sheet.write(row_pos, 3, '', table_border)
                            sheet.write(row_pos, 4, count_inv, table_border)
                        else:
                            sheet.write(row_pos, 1, '', table_border)
                            sheet.write(row_pos, 2, '', table_border)
                            sheet.write(row_pos, 3, '', table_border)
                            sheet.write(row_pos, 4, '', table_border)

                        row_pos += 1
                        sheet.write(row_pos, 0, '')
                        row_pos += 1
                        sheet.merge_range(row_pos, 0, row_pos, 4,
                                          'For the purpose of the audit of our accounts, we would be grateful if you could confirm the correctness of the above balance directly to our Chief Accountant at the following Phone no-09979930129.If we do not get reply from you within the 7 working days from the date of receipt of the statement, we will assume that the balance listed statements are correct.')
                        sheet.set_row(row_pos, 63)
                        row_pos += 1
                        sheet.write(row_pos, 0, 'Thank you for your co-operation.')
                        row_pos += 1
                        sheet.write(row_pos, 0, '')
                        row_pos += 1
                        sheet.merge_range(row_pos, 0, row_pos, 4,
                                          'Yours faithfully, ______________________				', normal_bold)
                        row_pos += 1
                        sheet.write(row_pos, 0, '')
                        row_pos += 1

                        sheet.write(row_pos, 0, '', up_border)
                        sheet.write(row_pos, 1, '', up_border)
                        sheet.write(row_pos, 2, '', up_border)
                        sheet.write(row_pos, 3, '', up_border)
                        sheet.write(row_pos, 4, '', right_bottom_up)

                        row_pos += 1

                        sheet.merge_range(row_pos, 0, row_pos, 4, 'Reply from addressee', format_title)
                        sheet.write(row_pos, 4, '', right_bottom)

                        row_pos += 1

                        sheet.write(row_pos, 0, '         I/We confirm that the above balance is correct.')
                        sheet.write(row_pos, 3, 'Signature    :')
                        sheet.write(row_pos, 4, '', right_bottom)

                        row_pos += 1

                        sheet.write(row_pos, 0, '         I/We confirm that the above balance is incorrect.')
                        sheet.write(row_pos, 3, 'Name            :')
                        sheet.write(row_pos, 4, '', right_bottom)

                        row_pos += 1

                        sheet.write(row_pos, 3, ' Position      : ')
                        sheet.write(row_pos, 4, '', right_bottom)

                        row_pos += 1

                        sheet.write(row_pos, 3, ' Date              : ')
                        sheet.write(row_pos, 4, '', right_bottom)

                        row_pos += 1

                        sheet.write(row_pos, 0, 'Company/Clinic Name', up_border)
                        sheet.write(row_pos, 1, '', up_border)
                        sheet.write(row_pos, 3, ' Ref                : ')
                        sheet.write(row_pos, 4, '', right_bottom)

                        row_pos += 1

                        sheet.write(row_pos, 0, '', bottom_border)
                        sheet.write(row_pos, 1, '', bottom_border)
                        sheet.write(row_pos, 2, '', bottom_border)
                        sheet.write(row_pos, 3, '', bottom_border)
                        sheet.write(row_pos, 4, '', right_bottom)


        workbook.close()
        output.seek(0)
        result = base64.b64encode(output.read())

        report_id = self.env['common.xlsx.out'].sudo().create(
            {'filedata': result, 'filename': 'AR Confirmation Report'})
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_document?model=common.xlsx.out&field=filedata&id=%s&filename=%s.xls' % (
                report_id.id, 'AR Confirmation Report.xls'),
            'target': 'new',
        }

        output.close()



