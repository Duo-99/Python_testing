from odoo import models, fields
from datetime import datetime
import time
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare, is_html_empty
from collections import defaultdict
from markupsafe import Markup
from odoo.tools import html2plaintext


class Repair(models.Model):
    _inherit = 'repair.order'

    plain_text = fields.Char(compute='_compute_plain_text', string='Internal Notes')
    quo_text = fields.Char(compute='_compute_quo_text', string='Quotation Notes')

    payment_state = fields.Selection(related='invoice_id.payment_state')
    create_date = fields.Date(string='Creation Date', readonly=True, index=True)

    order_type_id = fields.Many2one('order.type', string="Order Type")
    ca_category = fields.Many2one('ca.category', string="CA Category")
    email = fields.Char(related='user_id.partner_id.email')
    phone = fields.Char(related='user_id.partner_id.phone')
    # warranty_status=fields.Selection([('in_warranty','In Warranty'),('no_warranty','No Warranty')],tracking=True)
    product_model = fields.Char('Model')
    installation_date = fields.Date(string="Installation Date")
    completed_date = fields.Date(string="Completed Date")
    installation_department = fields.Char()
    street = fields.Char('Street', related="partner_id.street")
    street2 = fields.Char('Street 2', related="partner_id.street2")
    township = fields.Char("Township", related="partner_id.township.name")
    city = fields.Char("City", related="partner_id.city_id.name")
    state_name = fields.Char("State", related="partner_id.state.name")
    country = fields.Char("Country", related="partner_id.country_id.name")
    customer_phone = fields.Char("Phone", related="partner_id.phone")
    customer_mobile = fields.Char("Mobile", related="partner_id.mobile")
    customer_email = fields.Char("Email", related="partner_id.email")
    request_types = fields.Selection(
        [('field_service', 'Field Service'), ('inhouse', 'Inhouse'), ('on_call', 'On Call')], tracking=True)
    field_services = fields.Selection([('service_engineer', 'Engineer'), ('service_application', 'Application')],
                                      tracking=True)
    # field Service Eng
    assign_service_eng = fields.Many2many('res.partner', string="Assign Name")
    service_job = fields.Selection([('service_site', 'Site Survey'), ('service_installation', 'Installation'),
                                    ('service_maintenance', 'Maintenance'),
                                    ('service_repair', 'Repair'), ('service_replace', 'Replace'),
                                    ('service_ats', 'Analytical Trouble Shooting'),
                                    ('service_usr_training', 'User Training'), ('service_others', 'Others')],
                                   tracking=True)
    # field Service Application
    assign_service_app = fields.Many2one('res.partner', string="Assign Name")
    app_job = fields.Selection([('service_app_install', 'Installation'),
                                ('service_app_usr', 'User Training'),
                                ('service_app_ats', 'Analytical Trouble Shooting'),
                                ('service_app_ealu', 'Evaluation'),
                                ('service_app_other', 'Other')], tracking=True)

    # Inhouse service
    inhouse_services = fields.Selection([('inhouse_engineer', 'Engineer'), ('inhouse_application', 'Application')],
                                        tracking=True)
    assign_inhouse_eng = fields.Many2one('res.partner', string="Assign Name")
    inhouse_eng_job = fields.Selection([('inhouse_eng_repair', 'Repair'), ('inhouse_eng_refurbish', 'Refurbish'),
                                        ('inhouse_eng_func_testing', 'Functionality testing'),
                                        ('inhouse_eng_others', 'Others')], tracking=True)

    assign_inhouse_app = fields.Many2one('res.partner', string="Assign Name")
    inhouse_app_job = fields.Selection([('inhouse_app_func_testing', 'Functionality testing'),
                                        ('inhouse_app_ealu', 'Evaluation'),
                                        ('inhouse_app_ats', 'Analytical Trouble Shooting'),
                                        ('inhouse_app_other', 'Other')], tracking=True)
    injured_ans = fields.Selection([('yes', 'Yes'),
                                    ('no', 'No')], tracking=True)
    import_request = fields.Selection([('out_of_box_failure_equipment', 'Out of Box Failure Equipment'),
                                       ('out_of_box_failure_parts', 'Out of Box Failure Parts'),
                                       ('batch_failure', 'Batch Failure'),
                                       ('none', 'None')], tracking=True)
    correction = fields.Text(string="Correction")
    trouble_hq = fields.Selection([('always', 'Always'),
                                   ('intermittent', 'Intermittent'),
                                   ('random', 'Random')], tracking=True)
    phenomenon_of_problem_note = fields.Text(string="Technician Notes:")
    error_msg_note = fields.Text(string="Technician Notes:")
    solve_the_problem = fields.Text(string="Technician Notes:")
    sale_order_id = fields.Many2one('sale.order', 'Sale Order', copy=False,
                                    help="Sale Order from which the product to be repaired comes from.",
                                    domain="[('partner_id','=',partner_id),('state','=','sale'),('sale_order_lines.product_id','=',product_id),"
                                           "('invoice_status','=','invoiced')]",
                                    )
    warranty_status = fields.Selection([('in_warranty', 'In Warranty'), ('no_warranty', 'No Warranty')], tracking=True,
                                       default='no_warranty', )
    calibration = fields.Selection([('Pass', 'Pass'), ('Fail', 'Fail')], tracking=True, string='Calibration')
    qc_status = fields.Selection([('<1SD', '<1SD'), ('<2SD', '<2SD')], tracking=True, string='QC status')
    test_run = fields.Selection([('OK', 'OK'), ('not OK', 'not OK')], tracking=True, string='Test Run')
    precision_test = fields.Char(string='Precision Test(CV%)')
    analyzer_type = fields.Char(string='Analyzer Type')
    install_train_date = fields.Date('Date')
    wrt_start_date = fields.Date('Warranty Start Date')
    wrt_end_date = fields.Date('Warranty End Date')
    anal_condition = fields.Selection([('Good', 'Good'), ('Bad', 'Bad'), ('Damaged', 'Damaged'), ('Broken', 'Broken')],
                                      tracking=True, string='Analyzer condition')
    acc = fields.Selection([('complete', 'complete'), ('incomplete', 'incomplete')], tracking=True,
                           string='Accessories')
    acc_note = fields.Char(string='Accessories Note')
    test_run_status = fields.Selection([('satisfactory', 'satisfactory'), ('unsatisfactory', 'unsatisfactory')],
                                       tracking=True, string='Test Run Status')
    app_train = fields.Selection([('provided completely', 'provided completely'), ('incomplete', 'incomplete')],
                                 tracking=True, string='Application Training')
    ope_train = fields.Selection(
        [('satisfied', 'satisfied'), ('unsatisfied', 'unsatisfied'), ('required again', 'required again')],
        tracking=True, string='Operation Training')

    pricelist_id = fields.Many2one(
        'product.pricelist', 'Pricelist',
        domain=[('is_repair_pricelist', '=', True),],
        help='Pricelist of the selected partner.', check_company=True)



    invoice_method = fields.Selection(
        selection='_get_two_invoice_method', string="Invoice Method",
        default='after_repair', index=True, readonly=True, required=True,
        states={'draft': [('readonly', False)]},
        help='Selecting \'Before Repair\' or \'After Repair\' will allow you to generate invoice before or after the repair is done respectively. \'No invoice\' means you don\'t want to generate invoice for this repair order.')

    @api.depends('internal_notes')
    def _compute_plain_text(self):
        for record in self:
            record.plain_text = html2plaintext(record.internal_notes)

    @api.depends('quotation_notes')
    def _compute_quo_text(self):
        for record in self:
            record.quo_text = html2plaintext(record.quotation_notes)

    def _get_two_invoice_method(self):
        selection = [
            ("none", "No Invoice"),
            ("after_repair", "After Repair")
        ]
        return selection

    @api.onchange('sale_order_id')
    def wt_state(self):
        if self.sale_order_id:
            for rec in self:
                days_difference = (datetime.today() - rec.sale_order_id.date_order).days
                if days_difference <= 365:
                    rec.warranty_status = 'in_warranty'
                else:
                    rec.warranty_status = 'no_warranty'


    def _create_invoices(self, group=False):
        """ Creates invoice(s) for repair order.
        @param group: It is set to true when group invoice is to be generated.
        @return: Invoice Ids.
        """
        grouped_invoices_vals = {}
        repairs = self.filtered(lambda repair: repair.state not in ('draft', 'cancel')
                                               and not repair.invoice_id
                                               and repair.invoice_method != 'none')
        for repair in repairs:
            repair = repair.with_company(repair.company_id)
            partner_invoice = repair.partner_invoice_id or repair.partner_id
            if not partner_invoice:
                raise UserError(_('You have to select an invoice address in the repair form.'))

            narration = repair.quotation_notes
            currency = repair.pricelist_id.currency_id
            company = repair.env.company

            journal = repair.env['account.move'].with_context(move_type='out_invoice')._get_default_journal()
            if not journal:
                raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (company.name, company.id))

            if (partner_invoice.id, currency.id, company.id) not in grouped_invoices_vals:
                grouped_invoices_vals[(partner_invoice.id, currency.id, company.id)] = []
            current_invoices_list = grouped_invoices_vals[(partner_invoice.id, currency.id, company.id)]

            if not group or len(current_invoices_list) == 0:
                fpos = self.env['account.fiscal.position'].get_fiscal_position(partner_invoice.id, delivery_id=repair.address_id.id)
                invoice_vals = {
                    'move_type': 'out_invoice',
                    'partner_id': partner_invoice.id,
                    'partner_shipping_id': repair.address_id.id,
                    'currency_id': currency.id,
                    'narration': narration if not is_html_empty(narration) else '',
                    'invoice_origin': repair.name,
                    'repair_ids': [(4, repair.id)],
                    'invoice_line_ids': [],
                    'fiscal_position_id': fpos.id
                }
                if partner_invoice.property_payment_term_id:
                    invoice_vals['invoice_payment_term_id'] = partner_invoice.property_payment_term_id.id
                current_invoices_list.append(invoice_vals)
            else:
                # if group == True: concatenate invoices by partner and currency
                invoice_vals = current_invoices_list[0]
                invoice_vals['invoice_origin'] += ', ' + repair.name
                invoice_vals['repair_ids'].append((4, repair.id))
                if not is_html_empty(narration):
                    if  is_html_empty(invoice_vals['narration']):
                        invoice_vals['narration'] = narration
                    else:
                        invoice_vals['narration'] += Markup('<br/>') + narration

            # Create invoice lines from operations.
            for operation in repair.operations.filtered(lambda op: op.type == 'add'):
                if group:
                    name = repair.name + '-' + operation.name
                else:
                    name = operation.name

                account = operation.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=fpos)['income']
                if not account:
                    raise UserError(_('No account defined for product "%s".', operation.product_id.name))

                invoice_line_vals = {
                    'name': name,
                    'account_id': account.id,
                    'quantity': operation.product_uom_qty,
                    'tax_ids': [(6, 0, operation.tax_id.ids)],
                    'product_uom_id': operation.product_uom.id,
                    'price_unit': operation.price_unit,
                    'product_id': operation.product_id.id,
                    'repair_line_ids': [(4, operation.id)],
                    'discount': operation.discount,
                }

                if currency == company.currency_id:
                    balance = -(operation.product_uom_qty * operation.price_unit)
                    invoice_line_vals.update({
                        'debit': balance > 0.0 and balance or 0.0,
                        'credit': balance < 0.0 and -balance or 0.0,
                    })
                else:
                    amount_currency = -(operation.product_uom_qty * operation.price_unit)
                    balance = currency._convert(amount_currency, company.currency_id, company, fields.Date.today())
                    invoice_line_vals.update({
                        'amount_currency': amount_currency,
                        'debit': balance > 0.0 and balance or 0.0,
                        'credit': balance < 0.0 and -balance or 0.0,
                        'currency_id': currency.id,
                    })
                invoice_vals['invoice_line_ids'].append((0, 0, invoice_line_vals))

            # Create invoice lines from fees.
            for fee in repair.fees_lines:
                if group:
                    name = repair.name + '-' + fee.name
                else:
                    name = fee.name

                if not fee.product_id:
                    raise UserError(_('No product defined on fees.'))

                account = fee.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=fpos)['income']
                if not account:
                    raise UserError(_('No account defined for product "%s".', fee.product_id.name))

                invoice_line_vals = {
                    'name': name,
                    'account_id': account.id,
                    'quantity': fee.product_uom_qty,
                    'tax_ids': [(6, 0, fee.tax_id.ids)],
                    'product_uom_id': fee.product_uom.id,
                    'price_unit': fee.price_unit,
                    'product_id': fee.product_id.id,
                    'repair_fee_ids': [(4, fee.id)],
                    'discount': fee.discount,
                }

                if currency == company.currency_id:
                    balance = -(fee.product_uom_qty * fee.price_unit)
                    invoice_line_vals.update({
                        'debit': balance > 0.0 and balance or 0.0,
                        'credit': balance < 0.0 and -balance or 0.0,
                    })
                else:
                    amount_currency = -(fee.product_uom_qty * fee.price_unit)
                    balance = currency._convert(amount_currency, company.currency_id, company,
                                                fields.Date.today())
                    invoice_line_vals.update({
                        'amount_currency': amount_currency,
                        'debit': balance > 0.0 and balance or 0.0,
                        'credit': balance < 0.0 and -balance or 0.0,
                        'currency_id': currency.id,
                    })
                invoice_vals['invoice_line_ids'].append((0, 0, invoice_line_vals))

        # Create invoices.
        invoices_vals_list_per_company = defaultdict(list)
        for (partner_invoice_id, currency_id, company_id), invoices in grouped_invoices_vals.items():
            for invoice in invoices:
                invoices_vals_list_per_company[company_id].append(invoice)

        for company_id, invoices_vals_list in invoices_vals_list_per_company.items():
            # VFE TODO remove the default_company_id ctxt key ?
            # Account fallbacks on self.env.company, which is correct with with_company
            self.env['account.move'].with_company(company_id).with_context(default_company_id=company_id, default_move_type='out_invoice').create(invoices_vals_list)

        repairs.write({'invoiced': True})
        repairs.mapped('operations').filtered(lambda op: op.type == 'add').write({'invoiced': True})
        repairs.mapped('fees_lines').write({'invoiced': True})

        return dict((repair.id, repair.invoice_id.id) for repair in repairs)





class RepairLine(models.Model):
    _inherit = 'repair.line'

    discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)

    @api.depends('price_unit', 'repair_id', 'product_uom_qty', 'product_id', 'repair_id.invoice_method','discount')
    def _compute_price_subtotal(self):
        res = super(RepairLine,self)._compute_price_subtotal
        for line in self:
            taxes = line.tax_id.compute_all(line.price_unit * (1-(line.discount or 0.0)/100.0), line.repair_id.pricelist_id.currency_id,
                                            line.product_uom_qty, line.product_id, line.repair_id.partner_id)
            line.price_subtotal = taxes['total_excluded']

        return res

class RepairFee(models.Model):
    _inherit = 'repair.fee'

    discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)

    @api.depends('price_unit', 'repair_id', 'product_uom_qty', 'product_id','discount')
    def _compute_price_subtotal(self):
        res = super(RepairFee,self)._compute_price_subtotal
        for fee in self:
            taxes = fee.tax_id.compute_all(fee.price_unit * (1-(fee.discount or 0.0)/100.0), fee.repair_id.pricelist_id.currency_id, fee.product_uom_qty, fee.product_id, fee.repair_id.partner_id)
            fee.price_subtotal = taxes['total_excluded']
        return res









