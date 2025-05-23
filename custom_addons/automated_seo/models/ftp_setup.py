import base64
import os
import tempfile
import subprocess


def transfer_file_via_scp(page_name, file_data):
    temp_file = None
    final_path = None

    try:
        # Create temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.php')

        if not file_data:
            return False

        if isinstance(file_data, bytes):
            # Write content to temp file
            file_content = base64.b64decode(file_data)
            temp_file.write(file_content)
            temp_file.close()

            # Setup paths
            target_host = "u973764812@77.37.36.187"
            base_path = "/home/u973764812/domains/automatedseo.bacancy.com/public_html"
            target_path = base_path
            path = os.path.dirname(page_name)

            # Create local temp directory if needed
            temp_dir = os.path.dirname(os.path.join(tempfile.gettempdir(), page_name))
            os.makedirs(temp_dir, exist_ok=True)

            # Setup final path and rename
            final_path = os.path.join(tempfile.gettempdir(), page_name)
            os.rename(temp_file.name, final_path)

            # Append subdirectories to target path
            if path:
                target_path += f"/{path}"
                # Check if directory exists and create if needed
                ssh_key_path = os.path.expanduser('~/.ssh/seoserver')
                ssh_command = [
                    'ssh',
                    '-i', ssh_key_path,
                    '-p', '65002',
                    target_host,
                    f'mkdir -p {target_path}'
                ]

                # Run directory creation command
                ssh_result = subprocess.run(ssh_command, capture_output=True, text=True)
                if ssh_result.returncode != 0:
                    print(f"Failed to create directory: {ssh_result.stderr}")
                    return False

            # Execute SCP
            ssh_key_path = os.path.expanduser('~/.ssh/seoserver')
            scp_command = [
                'scp',
                '-i', ssh_key_path,
                '-P', '65002',
                final_path,
                f"{target_host}:{target_path}"
            ]

            result = subprocess.run(scp_command, capture_output=True, text=True)

            return result.returncode == 0

        return False

    except Exception as e:
        print(f"Error in file transfer: {str(e)}")
        return False

    finally:
        # Cleanup
        if final_path and os.path.exists(final_path):
            try:
                os.unlink(final_path)
            except:
                pass