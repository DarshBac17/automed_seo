
import subprocess
import tempfile
import base64

def transfer_file_via_scp(page_name, file_data, page_version=None):
    try:      
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.php')
        if file_data:
            try:
                if isinstance(file_data, bytes):
                    file_content = base64.b64decode(file_data)
                    temp_file.write(file_content)
                    temp_file.close()
                else:
                    return False
            except Exception as e:
                print(f"Error writing file: {str(e)}")
                return False
        target_dir = "bacancy@35.202.140.10:/home/pratik.panchal/temp/html"
        target_file = f"{page_name}.php"
        target_path = f"{target_dir}/{target_file}"
        scp_command = ['scp', temp_file.name, target_path]
        result = subprocess.run(
            scp_command,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"File transferred successfully")
            return True
        else:
            print(f"Transfer failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error during transfer: {str(e)}")
        return False
