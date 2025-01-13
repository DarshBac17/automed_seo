from odoo import models, fields, api, tools
import subprocess
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import subprocess
import threading

_logger = logging.getLogger(__name__)

class RemoteFolders(models.Model):
    _name = 'automated_seo.remote_folders'
    _description = 'Remote Folders'
    _rec_name = 'name'

    name = fields.Char(string='Folder Name', required=True)
    display_name = fields.Char(string='Display Name', compute='_compute_display_name', store=True)
    path = fields.Char(string='Full Path', compute='_compute_path')
    file_ids = fields.One2many('automated_seo.remote_files', 'folder_id', string='Files')

    @api.depends('name')
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.name.upper()

    @api.depends('name')
    def _compute_path(self):
        base_path = '/home/pratik.panchal/temp/html'
        for record in self:
            record.path = f"{base_path}/{record.name}" if record.name != 'html' else base_path

    def _has_php_files(self, folder_path):
        """Check if folder contains PHP files"""
        try:
            ssh_command = ['ssh', 'bacancy@35.202.140.10', f'ls -1 {folder_path}/*.php']
            result = subprocess.run(ssh_command, capture_output=True, text=True)
            return result.returncode == 0 and bool(result.stdout.strip())
        except Exception:
            return False
    
    @api.model
    def sync_folders(self):
        base_path = '/home/pratik.panchal/temp/html'
        try:
            ssh_command = ['ssh', 'bacancy@35.202.140.10', f'ls -l {base_path}']
            result = subprocess.run(ssh_command, capture_output=True, text=True)
            
            if result.returncode == 0:
                items = result.stdout.strip().split('\n')[1:]
                # Create HTML folder if not exists
                html_folder = self.search([('name', '=', 'html')], limit=1)
                if not html_folder:
                    self.create({'name': 'html'})
                    
                for item in items:
                    if item.startswith('d'):
                        folder_name = item.split()[-1]
                        folder_path = f"{base_path}/{folder_name}"
                    
                    if self._has_php_files(folder_path):
                        if not self.search([('name', '=', folder_name)]):
                            self.create({'name': folder_name})      
            return True
        except Exception as e:
            _logger.error(f"Error syncing folders: {str(e)}")
            return False

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('display_name', operator, name)]
        return self.search(domain + args, limit=limit).name_get()

class RemoteFiles(models.Model):
    _name = 'automated_seo.remote_files'
    _description = 'Remote Files'
    _rec_name = 'name'

    name = fields.Char(string='File Name', required=True)
    folder_id = fields.Many2one('automated_seo.remote_folders', string='Folder', required=True)
    is_processed = fields.Boolean(default=False)
    create_date = fields.Datetime('Created On', default=fields.Datetime.now)

    @api.onchange('folder_id')
    def _onchange_folder(self):
        if self.folder_id and self.folder_id.path:
            try:
                ssh_command = ['ssh', 'bacancy@35.202.140.10', f'ls -1 {self.folder_id.path}/*.php']
                result = subprocess.run(ssh_command, capture_output=True, text=True)
                if result.returncode == 0:
                    files = result.stdout.strip().split('\n')
                    return {'domain': {'name': [('name', 'in', [f.split('/')[-1] for f in files if f])]}}
            except Exception as e:
                _logger.error(f"Error fetching files: {str(e)}")
        return {'domain': {'name': []}}

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('folder_id.name', operator, name)]
        return self.search(domain + args, limit=limit).name_get()
    
    def _sync_folder_files(self, folder, timeout=10):
        try:
            ssh_command = ['ssh', '-o', 'ConnectTimeout=5', 'bacancy@35.202.140.10', 
                          f'ls -1 {folder.path}/*.php']
            result = subprocess.run(ssh_command, capture_output=True, text=True, 
                                 timeout=timeout)
            
            if result.returncode == 0:
                files = [f for f in result.stdout.strip().split('\n') if f]
                for file_path in files:
                    file_name = file_path.split('/')[-1]
                    existing = self.search([
                        ('name', '=', file_name),
                        ('folder_id', '=', folder.id)
                    ])
                    if not existing:
                        self.create({
                            'name': file_name,
                            'folder_id': folder.id
                        })
            return True
        except subprocess.TimeoutExpired:
            _logger.error(f"Timeout syncing files for folder {folder.name}")
            return False
        except Exception as e:
            _logger.error(f"Error syncing files for folder {folder.name}: {str(e)}")
            return False
        
    @api.model
    def sync_files(self):
        """Sync PHP files for all folders using parallel processing"""
        folders = self.env['automated_seo.remote_folders'].search([])
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            results = list(executor.map(self._sync_folder_files, folders))
            
        return all(results)
                        