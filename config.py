from openerp import models, fields, api

class sacco_settings(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'sacco.settings'

    module_sacco_approvals = fields.Boolean(string = 'Uses Approvals')
