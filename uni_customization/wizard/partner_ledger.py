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
    _inherit = "ins.partner.ledger"

    def get_totals(self):

        total_debit = 0.0
        total_credit = 0.0
        total_balance = 0.0
        company_currency_id = self.env.company.currency_id
        symbol = company_currency_id.symbol
        position = company_currency_id.position

        account_lines = self.process_data()
        for line in account_lines:
            total_debit += float(account_lines[line].get('debit'))
            total_credit += float(account_lines[line].get('credit'))
            total_balance += float(account_lines[line].get('balance'))
        if position == 'after':
            totals = {
                'total_debit': (str(company_currency_id.round(total_debit)) + ' ' + symbol),
                'total_credit': (str(company_currency_id.round(total_credit)) + ' ' + symbol),
                'total_balance': (str(company_currency_id.round(total_balance)) + ' ' + symbol)}
        else:
            totals = {
                'total_debit': (symbol + ' ' + str(company_currency_id.round(total_debit))),
                'total_credit': (symbol + ' ' + str(company_currency_id.round(total_credit))),
                'total_balance': (symbol + ' ' + str(company_currency_id.round(total_balance)))}
        return totals

    def get_report_datas(self, default_filters={}):

        if self.validate_data():
            filters = self.process_filters()
            account_lines = self.process_data()
            totals = self.get_totals()
            return filters, account_lines, totals

    def action_pdf(self):
        filters, account_lines, totals = self.get_report_datas()
        del totals
        return self.env.ref(
            'account_dynamic_reports'
            '.action_print_partner_ledger').with_context(landscape=True).report_action(
            self, data={'Ledger_data': account_lines,
                        'Filters': filters
                        })

    def action_xlsx(self):
        data = self.read()[0]
        # print('@@@@@@@@@@@', data)
        # print('###########', self.read())

        # Initialize
        #############################################################
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Partner Ledger')
        sheet.set_zoom(95)
        sheet_2 = workbook.add_worksheet('Filters')
        sheet_2.protect()

        # Get record and data
        record = self.env['ins.partner.ledger'].browse(data.get('id', [])) or False
        filter, account_lines, totals = record.get_report_datas()

        # Formats
        ############################################################
        sheet.set_column(0, 0, 12)
        sheet.set_column(1, 1, 12)
        sheet.set_column(2, 2, 30)
        sheet.set_column(3, 3, 18)
        sheet.set_column(4, 4, 30)
        sheet.set_column(5, 5, 13)
        sheet.set_column(6, 6, 13)
        sheet.set_column(7, 7, 13)

        sheet_2.set_column(0, 0, 35)
        sheet_2.set_column(1, 1, 25)
        sheet_2.set_column(2, 2, 25)
        sheet_2.set_column(3, 3, 25)
        sheet_2.set_column(4, 4, 25)
        sheet_2.set_column(5, 5, 25)
        sheet_2.set_column(6, 6, 25)

        sheet.freeze_panes(4, 0)

        sheet.screen_gridlines = False
        sheet_2.screen_gridlines = False
        sheet_2.protect()

        format_title = workbook.add_format({
            'bold': True,
            'align': 'center',
            'font_size': 12,
            'font': 'Arial',
            'border': False
        })
        format_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
            # 'border': True
        })
        content_header = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'border': True,
            'font': 'Arial',
        })
        content_header_date = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'border': True,
            'align': 'center',
            'font': 'Arial',
        })
        line_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            'top': True,
            'bottom': True,
            'font': 'Arial',
        })
        line_header_light = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'text_wrap': True,
            'font': 'Arial',
            'valign': 'top'
        })
        line_header_light_date = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
        })
        line_header_light_initial = workbook.add_format({
            'italic': True,
            'font_size': 10,
            'align': 'center',
            'bottom': True,
            'font': 'Arial',
            'valign': 'top'
        })
        line_header_light_initial_bold = workbook.add_format({
            'bold': True,
            'italic': True,
            'font_size': 10,
            'align': 'center',
            'bottom': True,
            'font': 'Arial',
            'valign': 'top'
        })
        line_header_light_ending = workbook.add_format({
            'italic': True,
            'font_size': 10,
            'align': 'center',
            'top': True,
            'font': 'Arial',
            'valign': 'top'
        })
        line_header_light_ending_bold = workbook.add_format({
            'bold': True,
            'italic': True,
            'font_size': 10,
            'align': 'center',
            'bottom': True,
            'font': 'Arial',
            'valign': 'top'
        })
        lang = self.env.user.lang
        lang_id = self.env['res.lang'].search([('code', '=', lang)])[0]
        currency_id = self.env.user.company_id.currency_id
        symbol = self.env.company.currency_id.symbol  # customized
        position = self.env.company.currency_id.position  # customized
        round = self.env.company.currency_id.round
        line_header.num_format = currency_id.excel_format
        line_header_light.num_format = currency_id.excel_format
        line_header_light_initial.num_format = currency_id.excel_format
        line_header_light_ending.num_format = currency_id.excel_format
        line_header_light_date.num_format = DATE_DICT.get(lang_id.date_format, 'dd/mm/yyyy')
        content_header_date.num_format = DATE_DICT.get(lang_id.date_format, 'dd/mm/yyyy')

        # Write data
        ################################################################
        row_pos_2 = 0
        row_pos = 0
        sheet.merge_range(0, 0, 0, 8, 'Partner Ledger' + ' - ' + data['company_id'][1], format_title)

        # Write filters
        sheet_2.write(row_pos_2, 0, _('Date from'), format_header)
        datestring = fields.Date.from_string(str(filter['date_from'])).strftime(lang_id.date_format)
        sheet_2.write(row_pos_2, 1, datestring or '', content_header_date)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Date to'), format_header)
        datestring = fields.Date.from_string(str(filter['date_to'])).strftime(lang_id.date_format)
        sheet_2.write(row_pos_2, 1, datestring or '', content_header_date)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Target moves'), format_header)
        sheet_2.write(row_pos_2, 1, filter['target_moves'], content_header)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Display accounts'), format_header)
        sheet_2.write(row_pos_2, 1, filter['display_accounts'], content_header)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Reconciled'), format_header)
        sheet_2.write(row_pos_2, 1, filter['reconciled'], content_header)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Initial Balance'), format_header)
        sheet_2.write(row_pos_2, 1, filter['initial_balance'], content_header)
        row_pos_2 += 1
        # Journals
        row_pos_2 += 2
        sheet_2.write(row_pos_2, 0, _('Journals'), format_header)
        j_list = ', '.join([lt or '' for lt in filter.get('journals')])
        sheet_2.write(row_pos_2, 1, j_list, content_header)
        # Partners
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Partners'), format_header)
        p_list = ', '.join([lt or '' for lt in filter.get('partners')])
        sheet_2.write(row_pos_2, 1, p_list, content_header)
        # Partner Tags
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Partner Tag'), format_header)
        p_list = ', '.join([lt or '' for lt in filter.get('categories')])
        sheet_2.write(row_pos_2, 1, p_list, content_header)
        # Accounts
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Accounts'), format_header)
        a_list = ', '.join([lt or '' for lt in filter.get('accounts')])
        sheet_2.write(row_pos_2, 1, a_list, content_header)

        # Write Ledger details
        row_pos += 3
        if filter.get('include_details', False):
            sheet.write(row_pos, 0, _('Date'),
                        format_header)
            sheet.write(row_pos, 1, _('JRNL'),
                        format_header)
            sheet.write(row_pos, 2, _('Account'),
                        format_header)
            # sheet.write(row_pos, 3, _('Ref'),
            #                         format_header)
            sheet.write(row_pos, 3, _('Move'),
                        format_header)
            sheet.write(row_pos, 4, _('Entry Label'),
                        format_header)
            sheet.write(row_pos, 5, _('Debit'),
                        format_header)
            sheet.write(row_pos, 6, _('Credit'),
                        format_header)
            sheet.write(row_pos, 7, _('Balance'),
                        format_header)
        else:
            sheet.merge_range(row_pos, 0, row_pos, 4, _('Partner'), format_header)
            sheet.write(row_pos, 5, _('Debit'),
                        format_header)
            sheet.write(row_pos, 6, _('Credit'),
                        format_header)
            sheet.write(row_pos, 7, _('Balance'),
                        format_header)

        if account_lines:
            for line in account_lines:
                if position == 'after':
                    row_pos += 1
                    sheet.merge_range(row_pos, 0, row_pos, 4, account_lines[line].get('name'), line_header)
                    sheet.write(row_pos, 5, str(round(float(account_lines[line].get('debit')))) + ' ' + symbol,
                                line_header)  # customized
                    sheet.write(row_pos, 6, str(round(float(account_lines[line].get('credit')))) + ' ' + symbol,
                                line_header)  # customized
                    sheet.write(row_pos, 7, str(round(float(account_lines[line].get('balance')))) + ' ' + symbol,
                                line_header)  # customized
                else:
                    row_pos += 1
                    sheet.merge_range(row_pos, 0, row_pos, 4, account_lines[line].get('name'), line_header)
                    sheet.write(row_pos, 5, symbol + ' ' + str(round(float(account_lines[line].get('debit')))),
                                line_header)  # customized
                    sheet.write(row_pos, 6, symbol + ' ' + str(round(float(account_lines[line].get('credit')))),
                                line_header)  # customized
                    sheet.write(row_pos, 7, symbol + ' ' + str(round(float(account_lines[line].get('balance')))),
                                line_header)  # customized

                    if filter.get('include_details', False):

                        count, offset, sub_lines = record.build_detailed_move_lines(offset=0, partner=line,
                                                                                    fetch_range=1000000)

                        for sub_line in sub_lines:
                            if sub_line.get('move_name') == 'Initial Balance':
                                if position == 'after':
                                    row_pos += 1
                                    sheet.write(row_pos, 4, sub_line.get('move_name'),
                                                line_header_light_initial_bold)
                                    sheet.write(row_pos, 5, str(round(float(sub_line.get('debit')))) + ' ' + symbol,
                                                line_header_light_initial)
                                    sheet.write(row_pos, 6, str(round(float(sub_line.get('credit')))) + ' ' + symbol,
                                                line_header_light_initial)
                                    sheet.write(row_pos, 7, str(round(float(sub_line.get('balance')))) + ' ' + symbol,
                                                line_header_light_initial)
                                else:
                                    row_pos += 1
                                    sheet.write(row_pos, 4, sub_line.get('move_name'),
                                                line_header_light_initial_bold)
                                    sheet.write(row_pos, 5, symbol + ' ' + str(round(float(sub_line.get('debit')))),
                                                line_header_light_initial)
                                    sheet.write(row_pos, 6, symbol + ' ' + str(round(float(sub_line.get('credit')))),
                                                line_header_light_initial)
                                    sheet.write(row_pos, 7, symbol + ' ' + str(round(float(sub_line.get('balance')))),
                                                line_header_light_initial)
                            elif sub_line.get('move_name') not in ['Initial Balance', 'Ending Balance']:
                                row_pos += 1
                                datestring = fields.Date.from_string(str(sub_line.get('ldate'))).strftime(
                                    lang_id.date_format)
                                sheet.write(row_pos, 0, datestring or '',
                                            line_header_light_date)
                                sheet.write(row_pos, 1, sub_line.get('lcode'),
                                            line_header_light)
                                sheet.write(row_pos, 2, sub_line.get('account_name') or '',
                                            line_header_light)
                                # sheet.write(row_pos, 3, sub_line.get('lref') or '',
                                #                         line_header_light)
                                sheet.write(row_pos, 3, sub_line.get('move_name'),
                                            line_header_light)
                                sheet.write(row_pos, 4, sub_line.get('lname') or '',
                                            line_header_light)
                                if position == 'after':
                                    sheet.write(row_pos, 5,
                                                str(round(float(sub_line.get('debit')))) + ' ' + symbol, line_header_light)
                                    sheet.write(row_pos, 6,
                                                str(round(float(sub_line.get('credit')))) + ' ' + symbol, line_header_light)
                                    sheet.write(row_pos, 7,
                                                str(round(float(sub_line.get('balance')))) + ' ' + symbol, line_header_light)

                                else:
                                    sheet.write(row_pos, 5,
                                                symbol + ' ' + str(round(float(sub_line.get('debit')))), line_header_light)
                                    sheet.write(row_pos, 6,
                                                symbol + ' ' + str(round(float(sub_line.get('credit')))), line_header_light)
                                    sheet.write(row_pos, 7,
                                                symbol + ' ' + str(round(float(sub_line.get('balance')))), line_header_light)

                            else:  # Ending Balance
                                row_pos += 1
                                sheet.write(row_pos, 4, sub_line.get('move_name'),
                                            line_header_light_ending_bold)
                                if position == 'after':
                                    sheet.write(row_pos, 5, str(round(float(account_lines[line].get('debit')))) + ' '
                                                + symbol, line_header_light_ending)
                                    sheet.write(row_pos, 6, str(round(float(account_lines[line].get('credit')))) + ' '
                                                + symbol, line_header_light_ending)
                                    sheet.write(row_pos, 7, str(round(float(account_lines[line].get('balance')))) + ' '
                                                + symbol, line_header_light_ending)
                                else:
                                    sheet.write(row_pos, 5,
                                                symbol + ' ' + str(round(float(account_lines[line].get('debit')))),
                                                line_header_light_ending)
                                    sheet.write(row_pos, 6,
                                                symbol + ' ' + str(round(float(account_lines[line].get('credit')))),
                                                line_header_light_ending)
                                    sheet.write(row_pos, 7,
                                                symbol + ' ' + str(round(float(account_lines[line].get('balance')))),
                                                line_header_light_ending)

        # Close and return
        #################################################################
        workbook.close()
        output.seek(0)
        result = base64.b64encode(output.read())
        report_id = self.env['common.xlsx.out'].sudo().create({'filedata': result, 'filename': 'PartnerLedger.xls'})

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_document?model=common.xlsx.out&field=filedata&id=%s&filename=%s.xls' % (
                report_id.id, 'Partner Ledger.xls'),
            'target': 'new',
        }

        output.close()
