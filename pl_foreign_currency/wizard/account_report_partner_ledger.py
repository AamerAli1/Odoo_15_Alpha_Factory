# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import UserError
import xlwt
from xlwt import *
import base64
from io import BytesIO
from collections import defaultdict


class AccountPartnerLedger(models.TransientModel):
    _inherit = "account.common.report"

    currency_id = fields.Many2one('res.currency', 'Currency')
    with_initial = fields.Boolean('With Initial Balance', default=True)
    result_selection = fields.Selection([('customer', 'Receivable Accounts'),
                                         ('supplier', 'Payable Accounts'),
                                         ('customer_supplier', 'Receivable and Payable Accounts')
                                         ], string="Partner's", required=True, default='customer')

    def print_report_fc(self):
        data = self[0].read()
        if 'active_ids' in self._context:
            data[0].update({'active_ids': self._context['active_ids']})
        return self.env.ref('pl_foreign_currency.action_report_partnerledger').report_action(self,
                                                                                             data={'form': data[0]})

    def export_excel_fc(self):
        data = self[0].read()
        if 'active_ids' in self._context:
            data[0].update({'active_ids': self._context['active_ids']})
        partner_id = self.env['res.partner'].browse(self._context.get('active_ids'))

        header_style = 'font: name Arial ; font:height 300; align: wrap on, vert center, horiz center'
        header_style1 = 'font: name Arial , bold on; font:height 225'
        number_style = 'align: wrap on, horiz right'
        number_style1 = 'align: wrap on, horiz right'

        report = xlwt.Workbook()
        sheet = report.add_sheet("Partner Ledger", cell_overwrite_ok=True)
        sheet.write_merge(1, 2, 4, 6, "Partner Ledger", Style.easyxf(header_style))

        partners = ''
        for part in partner_id:
            partners += part.name + ','
        partners = partners[:-1]
        x = 9
        first = True
        for partner in partner_id:

            sheet.write(4, 0, 'Company:')
            sheet.write(5, 0, self.env.company.name)
            sheet.write(4, 3, 'Partner:')
            sheet.write(5, 3, partner.name)
            sheet.write(4, 5, 'Target Moves:')
            sheet.write(5, 5, 'All Entries' if self.target_move == 'all' else 'All Posted Entries')
            if self.date_from:
                sheet.write(4, 7, 'Date From:')
                sheet.write(5, 7, self.date_from)
            if self.date_to:
                sheet.write(4, 9, 'Date To:')
                sheet.write(5, 9, self.date_to)

            sheet.write(7, 0, 'Date')
            sheet.write(7, 1, 'JRNL')
            sheet.write(7, 2, 'Ref')
            sheet.write(7, 3, 'Debit')
            sheet.write(7, 4, 'Credit')
            sheet.write(7, 5, 'Balance')

            datas = self.env['report.pl_foreign_currency.partnerledger'].get_lines({'form': data[0]}, partner)
            for line in datas:
                sheet.write_merge(x, x, 0, 2, line['cu'].name, Style.easyxf(header_style1))
                if len(partner_id.ids) > 1:
                    if not first:
                        x += 3
                    sheet.write(x, 0, partner.name, Style.easyxf(header_style1))
                    first = False
                if self.with_initial:
                    sheet.write(x + 1, 2, 'Initial Balance')
                    sheet.write(x + 1, 3, line['bal']['debit'])
                    sheet.write(x + 1, 4, line['bal']['credit'])
                    sheet.write(x + 1, 5, line['bal']['debit'] - line['bal']['credit'])
                bal = 0.0
                tot_debit = 0.0
                tot_credit = 0.0
                for l in line['lines']:
                    if l['date']:
                        bal = l['debit'] - l['credit'] + bal
                        jname = l['jname']
                        if l['ref']:
                            jname += '-' + l['ref']
                        if l['name']:
                            jname += '-' + l['name']
                        sheet.write(x + 2, 0, str(l['date']))
                        sheet.write(x + 2, 1, l['code'])
                        sheet.write(x + 2, 2, jname)
                        sheet.write(x + 2, 3, l['debit'])
                        sheet.write(x + 2, 4, l['credit'])
                        sheet.write(x + 2, 5, bal)
                        x += 1
                        tot_credit += l['credit']
                        tot_debit += l['debit']
                    sheet.write(x + 2, 2, 'Total', Style.easyxf(header_style1))
                    sheet.write(x + 2, 3, tot_debit, Style.easyxf(header_style1))
                    sheet.write(x + 2, 4, tot_credit, Style.easyxf(header_style1))
                    sheet.write(x + 2, 5, tot_debit - tot_credit, Style.easyxf(header_style1))
                    x += 3

        file_data = BytesIO()
        report.save(file_data)
        file_data.seek(0)
        data1 = file_data.read()
        attachment_id = self.env['ir.attachment'].create({
            'name': 'PartnerLedger.xls',
            'datas': base64.b64encode(data1),
        }).id

        record_id = self.env['partner.ledger.download'].create(
            {'excel_file': base64.b64encode(data1), 'file_name': 'PartnerLedger.xls'}, )

        return {'view_mode': 'form',
                'res_id': record_id.id,
                'res_model': 'partner.ledger.download',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {'create': False, 'edit': False, 'delete': False}
                }


class wizard_excel_report(models.TransientModel):
    _name = "partner.ledger.download"

    excel_file = fields.Binary('Excel File')
    file_name = fields.Char('Excel File', size=64)


# class ReportPartnerLedger(models.AbstractModel):
#     _inherit = "account.partner.ledger"
#
#     @api.model
#     def _get_query_sums(self, options, expanded_partner=None):
#         ''' Construct a query retrieving all the aggregated sums to build the report. It includes:
#         - sums for all partners.
#         - sums for the initial balances.
#         :param options:             The report options.
#         :param expanded_partner:    An optional res.partner record that must be specified when expanding a line
#                                     with of without the load more.
#         :return:                    (query, params)
#         '''
#         params = []
#         queries = []
#
#         if expanded_partner is not None:
#             domain = [('partner_id', '=', expanded_partner.id)]
#         else:
#             domain = []
#
#         # Create the currency table.
#         ct_query = self.env['res.currency']._get_query_currency_table(options)
#
#         # Get sums for all partners.
#         # period: [('date' <= options['date_to']), ('date' >= options['date_from'])]
#         new_options = self._get_options_sum_balance(options)
#         tables, where_clause, where_params = self._query_get(new_options, domain=domain)
#         params += where_params
#         queries.append('''
#                 SELECT
#                     account_move_line.partner_id        AS groupby,
#                     'sum'                               AS key,
#                     SUM(ROUND(account_move_line.debit * currency_table.rate, currency_table.precision))   AS debit,
#                     SUM(ROUND(account_move_line.credit * currency_table.rate, currency_table.precision))  AS credit,
#                     SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)) AS balance,
#                     SUM(ROUND(account_move_line.amount_currency * currency_table.rate, currency_table.precision)) AS amount_currency
#                 FROM %s
#                 LEFT JOIN %s ON currency_table.company_id = account_move_line.company_id
#                 WHERE %s
#                 GROUP BY account_move_line.partner_id
#             ''' % (tables, ct_query, where_clause))
#
#         # Get sums for the initial balance.
#         # period: [('date' <= options['date_from'] - 1)]
#         new_options = self._get_options_initial_balance(options)
#         tables, where_clause, where_params = self._query_get(new_options, domain=domain)
#         params += where_params
#         queries.append('''
#                 SELECT
#                     account_move_line.partner_id        AS groupby,
#                     'initial_balance'                   AS key,
#                     SUM(ROUND(account_move_line.debit * currency_table.rate, currency_table.precision))   AS debit,
#                     SUM(ROUND(account_move_line.credit * currency_table.rate, currency_table.precision))  AS credit,
#                     SUM(ROUND(account_move_line.amount_currency * currency_table.rate, currency_table.precision)) AS amount_currency,
#                     SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)) AS balance
#                 FROM %s
#                 LEFT JOIN %s ON currency_table.company_id = account_move_line.company_id
#                 WHERE %s
#                 GROUP BY account_move_line.partner_id
#             ''' % (tables, ct_query, where_clause))
#
#         return ' UNION ALL '.join(queries), params
#
#     @api.model
#     def _get_sums_without_partner(self, options, expanded_partner=None):
#         ''' Get the sum of lines without partner reconciled with a line with a partner, grouped by partner. Those lines
#         should be considered as belonging the partner for the reconciled amount as it may clear some of the partner
#         invoice/bill and they have to be accounted in the partner balance.'''
#
#         params = []
#         if expanded_partner:
#             partner_clause = '= %s'
#             params = [expanded_partner.id]
#         else:
#             partner_clause = 'IS NOT NULL'
#
#         new_options = self._get_options_without_partner(options)
#         params = [options['date']['date_from']] + params + [options['date']['date_to']]
#         tables, where_clause, where_params = self._query_get(new_options, domain=[])
#         params += where_params
#
#         query = '''
#                 SELECT
#                     aml_with_partner.partner_id AS groupby,
#                     SUM(CASE WHEN aml_with_partner.balance > 0 THEN 0 ELSE partial.amount END) AS debit,
#                     SUM(CASE WHEN aml_with_partner.balance < 0 THEN 0 ELSE partial.amount END) AS credit,
#                     SUM(CASE WHEN aml_with_partner.balance > 0 THEN -partial.amount ELSE partial.amount END) AS balance,
#                     SUM(CASE WHEN aml_with_partner.amount_currency > 0 THEN aml_with_partner.amount_currency ELSE 0 END) AS amount_currency,
#                     CASE WHEN partial.max_date < %s THEN 'initial_balance' ELSE 'sum' END as key
#                 FROM {tables}, account_partial_reconcile partial, account_move_line aml_with_partner
#                 WHERE (account_move_line.id = partial.debit_move_id OR account_move_line.id = partial.credit_move_id)
#                    AND account_move_line.partner_id IS NULL
#                    AND (aml_with_partner.id = partial.debit_move_id OR aml_with_partner.id = partial.credit_move_id)
#                    AND aml_with_partner.partner_id {partner_clause}
#                    AND partial.max_date <= %s
#                    AND {where_clause}
#                 GROUP BY aml_with_partner.partner_id, key
#             '''.format(tables=tables, partner_clause=partner_clause, where_clause=where_clause)
#         return query, params
#
#     @api.model
#     def _do_query(self, options, expanded_partner=None):
#         ''' Execute the queries, perform all the computation and return partners_results,
#         a lists of tuple (partner, fetched_values) sorted by the table's model _order:
#             - partner is a res.parter record.
#             - fetched_values is a dictionary containing:
#                 - sum:                              {'debit': float, 'credit': float, 'balance': float}
#                 - (optional) initial_balance:       {'debit': float, 'credit': float, 'balance': float}
#                 - (optional) lines:                 [line_vals_1, line_vals_2, ...]
#         :param options:             The report options.
#         :param expanded_account:    An optional account.account record that must be specified when expanding a line
#                                     with of without the load more.
#         :param fetch_lines:         A flag to fetch the account.move.lines or not (the 'lines' key in accounts_values).
#         :return:                    (accounts_values, taxes_results)
#         '''
#
#         def assign_sum(row):
#             key = row['key']
#             fields = ['balance', 'debit', 'credit', 'amount_currency'] if key == 'sum' else ['balance']
#             if any(not company_currency.is_zero(row[field]) for field in fields):
#                 groupby_partners.setdefault(row['groupby'], defaultdict(lambda: defaultdict(float)))
#                 for field in fields:
#                     groupby_partners[row['groupby']][key][field] += row[field]
#
#         company_currency = self.env.company.currency_id
#
#         # flush the tables that gonna be queried
#         self.env['account.move.line'].flush(fnames=self.env['account.move.line']._fields)
#         self.env['account.move'].flush(fnames=self.env['account.move']._fields)
#         self.env['account.partial.reconcile'].flush(fnames=self.env['account.partial.reconcile']._fields)
#
#         # Execute the queries and dispatch the results.
#         query, params = self._get_query_sums(options, expanded_partner=expanded_partner)
#
#         groupby_partners = {}
#
#         self._cr.execute(query, params)
#         for res in self._cr.dictfetchall():
#             assign_sum(res)
#
#         # Fetch the lines of unfolded accounts.
#         unfold_all = options.get('unfold_all') or (self._context.get('print_mode') and not options['unfolded_lines'])
#         if expanded_partner or unfold_all or options['unfolded_lines']:
#             query, params = self._get_query_amls(options, expanded_partner=expanded_partner)
#             self._cr.execute(query, params)
#             for res in self._cr.dictfetchall():
#                 if res['partner_id'] not in groupby_partners:
#                     continue
#                 groupby_partners[res['partner_id']].setdefault('lines', [])
#                 groupby_partners[res['partner_id']]['lines'].append(res)
#
#             query, params = self._get_lines_without_partner(options, expanded_partner=expanded_partner)
#             self._cr.execute(query, params)
#             for row in self._cr.dictfetchall():
#                 # don't show lines of partners not expanded
#                 if row['partner_id'] in groupby_partners:
#                     groupby_partners[row['partner_id']].setdefault('lines', [])
#                     row['class'] = ' text-muted'
#                     groupby_partners[row['partner_id']]['lines'].append(row)
#                 if None in groupby_partners:
#                     # reconciled lines without partners are fetched to be displayed under the matched partner
#                     # and thus but be inversed to be displayed under the unknown partner
#                     none_row = row.copy()
#                     none_row['class'] = ' text-muted'
#                     none_row['debit'] = row['credit']
#                     none_row['credit'] = row['debit']
#                     none_row['amount_currency'] = row['amount_currency']
#                     none_row['balance'] = -row['balance']
#                     groupby_partners[None].setdefault('lines', [])
#                     groupby_partners[None]['lines'].append(none_row)
#
#         # correct the sums per partner, for the lines without partner reconciled with a line having a partner
#         query, params = self._get_sums_without_partner(options, expanded_partner=expanded_partner)
#         self._cr.execute(query, params)
#         total = total_debit = total_credit = total_initial_balance = total_currency = 0
#         for row in self._cr.dictfetchall():
#             key = row['key']
#             total_debit += key == 'sum' and row['debit'] or 0
#             total_credit += key == 'sum' and row['credit'] or 0
#             total_currency += key == 'sum' and row['amount_currency'] or 0
#             total_initial_balance += key == 'initial_balance' and row['balance'] or 0
#             total += key == 'sum' and row['balance'] or 0
#             if None not in groupby_partners and not (expanded_partner or unfold_all or options['unfolded_lines']):
#                 groupby_partners.setdefault(None, {})
#             if row['groupby'] not in groupby_partners:
#                 continue
#             assign_sum(row)
#
#         if None in groupby_partners:
#             if 'sum' not in groupby_partners[None]:
#                 groupby_partners[None].setdefault('sum', {'debit': 0, 'credit': 0, 'balance': 0})
#             if 'initial_balance' not in groupby_partners[None]:
#                 groupby_partners[None].setdefault('initial_balance', {'balance': 0})
#             # debit/credit are inversed for the unknown partner as the computation is made regarding the balance of the known partner
#             groupby_partners[None]['sum']['debit'] += total_credit
#             groupby_partners[None]['sum']['credit'] += total_debit
#             groupby_partners[None]['sum']['amount_currency'] += total_currency
#             groupby_partners[None]['sum']['balance'] -= total
#             groupby_partners[None]['initial_balance']['balance'] -= total_initial_balance
#
#         # Retrieve the partners to browse.
#         # groupby_partners.keys() contains all account ids affected by:
#         # - the amls in the current period.
#         # - the amls affecting the initial balance.
#         # Note a search is done instead of a browse to preserve the table ordering.
#         if expanded_partner:
#             partners = expanded_partner
#         elif groupby_partners:
#             partners = self.env['res.partner'].with_context(active_test=False).search(
#                 [('id', 'in', list(groupby_partners.keys()))])
#         else:
#             partners = []
#
#         # Add 'Partner Unknown' if needed
#         if None in groupby_partners.keys():
#             partners = [p for p in partners] + [None]
#         return [(partner, groupby_partners[partner.id if partner else None]) for partner in partners]
#
#     @api.model
#     def _get_report_line_partner(self, options, partner, initial_balance, debit, credit, balance, amount_currency):
#         company_currency = self.env.company.currency_id
#         unfold_all = self._context.get('print_mode') and not options.get('unfolded_lines')
#
#         columns = [
#             {'name': self.format_value(initial_balance), 'class': 'number'},
#             {'name': self.format_value(debit), 'class': 'number'},
#             {'name': self.format_value(credit), 'class': 'number'},
#         ]
#         if self.user_has_groups('base.group_multi_currency'):
#             columns.append({'name': self.format_value(amount_currency), 'class': 'number'})
#         columns.append({'name': self.format_value(balance), 'class': 'number'})
#
#         return {
#             'id': 'partner_%s' % (partner.id if partner else 0),
#             'partner_id': partner.id if partner else None,
#             'name': partner is not None and (partner.name or '')[:128] or _('Unknown Partner'),
#             'columns': columns,
#             'level': 2,
#             'trust': partner.trust if partner else None,
#             'unfoldable': not company_currency.is_zero(debit) or not company_currency.is_zero(credit),
#             'unfolded': 'partner_%s' % (partner.id if partner else 0) in options['unfolded_lines'] or unfold_all,
#             'colspan': 6,
#         }
#
#     @api.model
#     def _get_report_line_total(self, options, initial_balance, debit, credit, balance, amount_currency):
#         columns = [
#             {'name': self.format_value(initial_balance), 'class': 'number'},
#             {'name': self.format_value(debit), 'class': 'number'},
#             {'name': self.format_value(credit), 'class': 'number'},
#         ]
#         if self.user_has_groups('base.group_multi_currency'):
#             columns.append({'name': self.format_value(amount_currency), 'class': 'number'})
#         columns.append({'name': self.format_value(balance), 'class': 'number'})
#         return {
#             'id': 'partner_ledger_total_%s' % self.env.company.id,
#             'name': _('Total'),
#             'class': 'total',
#             'level': 1,
#             'columns': columns,
#             'colspan': 6,
#         }
#
#     @api.model
#     def _get_partner_ledger_lines(self, options, line_id=None):
#         ''' Get lines for the whole report or for a specific line.
#         :param options: The report options.
#         :return:        A list of lines, each one represented by a dictionary.
#         '''
#         lines = []
#         unfold_all = options.get('unfold_all') or (self._context.get('print_mode') and not options['unfolded_lines'])
#
#         expanded_partner = line_id and self.env['res.partner'].browse(int(line_id[8:]))
#         partners_results = self._do_query(options, expanded_partner=expanded_partner)
#
#         total_initial_balance = total_debit = total_credit = total_balance = total_amount_currency = 0.0
#         for partner, results in partners_results:
#             is_unfolded = 'partner_%s' % (partner.id if partner else 0) in options['unfolded_lines']
#
#             # res.partner record line.
#             partner_sum = results.get('sum', {})
#             partner_init_bal = results.get('initial_balance', {})
#
#             initial_balance = partner_init_bal.get('balance', 0.0)
#             debit = partner_sum.get('debit', 0.0)
#             credit = partner_sum.get('credit', 0.0)
#             amount_currency = partner_sum.get('amount_currency', 0.0)
#             balance = initial_balance + partner_sum.get('balance', 0.0)
#
#             lines.append(self._get_report_line_partner(options, partner, initial_balance, debit, credit, balance, amount_currency))
#
#             total_initial_balance += initial_balance
#             total_debit += debit
#             total_credit += credit
#             total_amount_currency += amount_currency
#             total_balance += balance
#
#             if unfold_all or is_unfolded:
#                 cumulated_balance = initial_balance
#
#                 # account.move.line record lines.
#                 amls = results.get('lines', [])
#
#                 load_more_remaining = len(amls)
#                 load_more_counter = self._context.get('print_mode') and load_more_remaining or self.MAX_LINES
#
#                 for aml in amls:
#                     # Don't show more line than load_more_counter.
#                     if load_more_counter == 0:
#                         break
#
#                     cumulated_init_balance = cumulated_balance
#                     cumulated_balance += aml['balance']
#                     lines.append(self._get_report_line_move_line(options, partner, aml, cumulated_init_balance,
#                                                                  cumulated_balance))
#
#                     load_more_remaining -= 1
#                     load_more_counter -= 1
#
#                 if load_more_remaining > 0:
#                     # Load more line.
#                     lines.append(self._get_report_line_load_more(
#                         options,
#                         partner,
#                         self.MAX_LINES,
#                         load_more_remaining,
#                         cumulated_balance,
#                     ))
#
#         if not line_id:
#             # Report total line.
#             lines.append(self._get_report_line_total(
#                 options,
#                 total_initial_balance,
#                 total_debit,
#                 total_credit,
#                 total_balance,
#                 total_amount_currency
#             ))
#         return lines
