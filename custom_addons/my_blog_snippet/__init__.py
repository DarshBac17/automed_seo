# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Ammu (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
from . import controller
from . import models
from odoo import api, SUPERUSER_ID

def add_test_data(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    BlogSnippet = env['blog.snippet']
    if not BlogSnippet.search([]):
        BlogSnippet.create([{
            'title': f'Test Blog {i}',
            'content': f'This is test content for blog {i}.'
        } for i in range(1, 6)])

# Add this function to your module's __init__.py