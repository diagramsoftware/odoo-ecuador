# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, SUPERUSER_ID

UPDATE_PARTNER_FIELDS = set(['firstname', 'lastname', 'user_id',
                             'address_home_id'])


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def split_name(self, name):
        clean_name = u" ".join(name.split(None)) if name else name
        return clean_name, False

    @api.cr_context
    def _auto_init(self, cr, context=None):
        super(HrEmployee, self)._auto_init(cr, context=context)
        self._update_employee_names(cr, SUPERUSER_ID, context=context)

    @api.model
    def _update_employee_names(self):
        employees = self.search([
            ('firstname', '=', ' '), ('lastname', '=', ' ')])

        for ee in employees:
            lastname, firstname = self.split_name(ee.name)
            ee.write({
                'firstname': firstname,
                'lastname': lastname,
            })

    @api.model
    def _update_partner_firstname(self, employee):
        partners = employee.mapped('user_id.partner_id')
        for partner in employee.mapped('address_home_id'):
            if partner not in partners:
                partners += partner
        partners.write({'firstname': employee.firstname,
                        'lastname': employee.lastname})

    @api.model
    def _get_name(self, lastname, firstname):
        return ' '.join([lastname, firstname])

    @api.one
    @api.onchange('firstname', 'lastname')
    def get_name(self):
        if self.firstname and self.lastname:
            self.name = self._get_name(self.lastname, self.firstname)

    def _firstname_default(self):
        return ' ' if self.env.context.get('module') else False

    firstname = fields.Char(
        "Firstname", default=_firstname_default)
    lastname = fields.Char(
        "Lastname", required=True, default=_firstname_default)
    identificador = fields.Char('Cédula', required=True,
                                size=10, default='9999999999')

    @api.model
    def create(self, vals):
        if vals.get('firstname') and vals.get('lastname'):
            vals['name'] = self._get_name(vals['lastname'], vals['firstname'])

        elif vals.get('name'):
            lastname, firstname = self.split_name(vals['name'])
            vals['lastname'] = lastname
            vals['firstname'] = firstname
        res = super(HrEmployee, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if vals.get('firstname') or vals.get('lastname'):
            lastname = vals.get('lastname') or self.lastname or ' '
            firstname = vals.get('firstname') or self.firstname or ' '
            vals['name'] = self._get_name(lastname, firstname)
        elif vals.get('name'):
            lastname, firstname = self.split_name(vals['name'])
            vals['lastname'] = lastname
            vals['firstname'] = firstname
        res = super(HrEmployee, self).write(vals)
#        if set(vals).intersection(UPDATE_PARTNER_FIELDS):
#            self._update_partner_firstname(self)
        return res
