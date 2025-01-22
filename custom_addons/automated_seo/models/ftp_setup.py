
import subprocess
import tempfile
import base64
import os

def transfer_file_via_scp(page_name, file_data):
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.php')
        if file_data:
            try:
                if isinstance(file_data, bytes):
                    file_content = base64.b64decode(file_data)
                    temp_file.write(file_content)

                    target_path = "u973764812@77.37.36.187:/home/u973764812/domains/automatedseo.bacancy.com/public_html"

                    path = os.path.dirname(page_name)

                    if path:
                        target_path += f"/{path}"

                    final_path = os.path.join(tempfile.gettempdir(), os.path.basename(page_name))
                    os.rename(temp_file.name, final_path)

                    temp_file.name = final_path
                    temp_file.close()

                    ssh_key_path='~/.ssh/seoserver'

                    scp_command = ['scp', '-i', os.path.expanduser(ssh_key_path),'-P', '65002', temp_file.name, target_path]
                    result = subprocess.run(
                        scp_command,
                        capture_output=True,
                        text=True
                    )

                    os.unlink(final_path)
                    if result.returncode == 0:
                        print(f"File transferred successfully")
                        return True
                    else:
                        print(f"Transfer failed: {result.stderr}")
                        return False

                else:
                    return False
            except Exception as e:
                print(f"Error writing file: {str(e)}")
                return False

    except Exception as e:
        print(f"Error during transfer: {str(e)}")
        return False
