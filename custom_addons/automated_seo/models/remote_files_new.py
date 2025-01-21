from odoo import models, fields, api, tools
import subprocess
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import subprocess
import threading

_logger = logging.getLogger(__name__)


class RemoteFiles(models.Model):
    _name = 'automated_seo.remote_files'
    _description = 'Remote Files'
    _rec_name = 'name'

    name = fields.Char(string='File Name', required=True)  # Changed to store relative path
    is_processed = fields.Boolean(default=False)
    full_path = fields.Char(string='Full Path', compute='_compute_full_path')
    create_date = fields.Datetime('Created On', default=fields.Datetime.now)

    @api.depends('name')
    def _compute_full_path(self):
        base_path = '/home/u973764812/domains/automatedseo.bacancy.com/public_html'
        for record in self:
            record.full_path = f"{base_path}/{record.name}" if record.name != 'html' else base_path


    @api.model
    def sync_remote_files(self, timeout=30):
        """
        Recursively sync all PHP files from remote server including their relative paths.

        Args:
            base_path (str): Base path to start recursive search
            timeout (int): Timeout in seconds for the SSH command

        Returns:
            bool: True if sync was successful, False otherwise
        """
        base_path = '/home/u973764812/domains/automatedseo.bacancy.com/public_html'
        try:
            # Command to find all PHP files recursively and get their paths relative to base_path
            find_command = (
                f"cd {base_path} && "
                "find . -type f -name '*.php' -printf '%P\\n'"
            )

            ssh_command = [
                'ssh',
                '-p','65002',
                '-o', 'ConnectTimeout=5',
                'u973764812@77.37.36.187',
                find_command
            ]

            result = subprocess.run(
                ssh_command,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if result.returncode != 0:
                _logger.error(f"Error executing SSH command: {result.stderr}")
                return False

            # Process the results
            file_paths = [
                path.strip()
                for path in result.stdout.split('\n')
                if path.strip()
            ]

            # Get existing files for this batch
            existing_files = self.search([
                ('name', 'in', file_paths)
            ]).mapped('name')

            # Filter out existing files
            new_files = [
                {'name': path}
                for path in file_paths
                if path not in existing_files
            ]

            if new_files:
                self.create(new_files)

            _logger.info(f"Successfully synced {len(file_paths)} PHP files")
            return True

        except subprocess.TimeoutExpired:
            _logger.error(f"Timeout while executing SSH command (>{timeout}s)")
            return False
        except Exception as e:
            _logger.error(f"Error syncing remote files: {str(e)}")
            return False