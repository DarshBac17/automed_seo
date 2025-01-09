from odoo import models, fields, api
import subprocess

class RemoteFiles(models.Model):
    _name = 'automated_seo.remote_files'
    _description = 'Remote Files'
    _rec_name = 'name'

    name = fields.Char(string='File Name', required=True)
    is_processed = fields.Boolean(default=False)
    create_date = fields.Datetime('Created On', default=fields.Datetime.now)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            records = self.search([('name', operator, name)] + args, limit=limit)
        else:
            records = self.search(args, limit=limit)
        return records.name_get()

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.name))
        return result

    @api.model
    def sync_remote_files(self):
        try:
            ssh_command = ['ssh', 'bacancy@35.202.140.10', 'ls -1 /home/pratik.panchal/temp/html']
            result = subprocess.run(ssh_command, capture_output=True, text=True)
            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                existing_files = self.search([]).mapped('name')
                
                # Add new files
                for file in files:
                    if file and file not in existing_files:
                        self.create({'name': file})
                        
                return True
        except Exception as e:
            return False