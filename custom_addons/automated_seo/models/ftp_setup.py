from ftplib import FTP
import os
import base64
import traceback

# try:
#     ftp = FTP('ip-172-31-18-5', timeout=10)
#     ftp.login('ubuntu')

#     print("Connected to FTP server successfully.")



#     ftp.retrlines("LIST")
# except Exception as e:
#     print(f"Error connecting to FTP server: {str(e)}")

# def push_changes_to_ftp(page_name, page_version, last_updated, user_id,user_name, file_data,
#                         ftp_host="bacancy-Vostro-3508", ftp_user="khushbu", ftp_pass="khushbu",
#                         target_dir="/home/bacancy/Desktop/automated_seo/temp"):
#     try:
#         # Initialize FTP connection
#         try:
#             ftp = FTP('35.202.140.10', timeout=10)
#             ftp.login('pratik.panchal')
#
#             print("Connected to FTP server successfully.")
#
#             target_file = f"{page_name}_{page_version}.php"
#             target_file_path = os.path.join(target_dir, target_file)
#
#             ftp.retrlines("LIST")
#         except Exception as e:
#             print(f"Error connecting to FTP server: {str(e)}")
#             return False
#
#         # Decode and write the binary data to a local file
#         if file_data:
#             try:
#                 decoded_data = None
#                 if isinstance(file_data, bytes):
#                     decoded_data = base64.b64decode(file_data)
#
#                 if decoded_data:
#                     with open(target_file_path, 'wb') as file:
#                         file.write(decoded_data)
#                     print(f"Decoded and saved file to {target_file_path}")
#                 else:
#                     return False
#             except Exception as e:
#                 print(f"Error writing file: {str(e)}")
#                 return False
#
#         # Upload the file to FTP server
#         with open(target_file_path, 'rb') as file:
#             ftp.storbinary(f"STOR {target_file}", file)
#         print(f"Uploaded {target_file} to FTP server.")
#
#         commit_message = (f"Page Update: {page_name}\n"
#                           f"Version: {page_version}\n"
#                           f"Last Updated: {last_updated}\n"
#                           f"User ID: {user_id}\n"
#                           f"User Name: {user_name}\n")
#
#         print(f"Changes uploaded with the following message:\n{commit_message}")
#
#         ftp.quit()
#         print(f"Successfully closed the FTP connection.")
#
#         return True
#     except Exception as e:
#         print(f"An error occurred: {str(e)}")
#         traceback.print_exc()
#         return False

import paramiko
from ftplib import FTP
import os

def connect_to_aws_ftp(host='ip-172-31-18-5', 
                       username='ubuntu',
                       key_path='/home/bacancy/Downloads/DT-993-Setup-Ubuntu-server-Meet-Patel.pem',
                       port=22):
    try:
        # Initialize SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Load private key
        key_path = os.path.expanduser(key_path)
        private_key = paramiko.RSAKey.from_private_key_file(key_path)
        
        # Connect to server
        ssh.connect(
            hostname=host,
            username=username,
            pkey=private_key,
            port=port
        )
        
        # Create SFTP client
        sftp = ssh.open_sftp()
        
        print(f"Successfully connected to {host}")
        return sftp, ssh
        
    except Exception as e:
        print(f"Connection failed: {str(e)}")
        return None, None

# Usage example
# if __name__ == "__main__":
    # sftp, ssh = connect_to_aws_ftp()
    
    # if sftp:
    #     print(sftp.listdir())
    #     sftp.close()
    #     ssh.close()

# import paramiko
# import os
# import base64
# import traceback

# def push_changes_to_server(page_name, page_version, last_updated, user_id, user_name, file_data,
#                           host="35.202.140.10", 
#                           username="pratik.panchal",
#                           password="your_password",  # Consider using env variables
#                           remote_path="/home/pratik.panchal/temp/html"):
#     try:
#         # Create SSH client
#         ssh = paramiko.SSHClient()
#         ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
#         # Connect to remote server
#         ssh.connect(host, username=username, password=password)
#         sftp = ssh.open_sftp()
        
#         # Prepare file name and paths
#         target_file = f"{page_name}_{page_version}.php"
#         local_path = f"/tmp/{target_file}"
#         remote_file_path = f"{remote_path}/{target_file}"
        
#         # Write data to local file
#         if file_data:
#             decoded_data = base64.b64decode(file_data) if isinstance(file_data, bytes) else file_data
#             with open(local_path, 'wb') as f:
#                 f.write(decoded_data)
        
#         # Upload file
#         sftp.put(local_path, remote_file_path)
        
#         # Cleanup
#         os.remove(local_path)
#         sftp.close()
#         ssh.close()
        
#         print(f"File transferred successfully to {remote_file_path}")
#         return True
        
#     except Exception as e:
#         print(f"Error during transfer: {str(e)}")
#         traceback.print_exc()
#         return False




# import paramiko

# # host='ip-172-31-18-5', 
# #                        username='',
# #                        key_path='',

# # Details
# pem_file_path = "/home/bacancy/Downloads/DT-993-Setup-Ubuntu-server-Meet-Patel.pem"  # Replace with the path to your .pem file
# server_ip = "65.0.83.186"  # Replace with your server's IP
# username = "ubuntu"  # Default for Amazon Linux; replace if using another distro
# local_file_path = "/home/bacancy/Downloads/angular-js-development_test.php"  # Path to the file you want to upload
# remote_directory = "/home/ubuntu"  # Directory on the server to upload the file to

# # Connect to the server using SSH
# try:
#     # Create an SSH client
#     ssh_client = paramiko.SSHClient()
#     ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
#     # Load the private key
#     private_key = paramiko.RSAKey.from_private_key_file(pem_file_path)
    
#     # Connect to the server
#     print(f"Connecting to {server_ip} as {username}...")
#     ssh_client.connect(hostname=server_ip, username=username, pkey=private_key)
#     print("Connected successfully!")

#     # Create an SFTP session
#     sftp = ssh_client.open_sftp()

#     # # Upload the file
#     remote_file_path = f"{remote_directory}/angular-js-development_test.php"  # Change filename if needed
#     print(f"Uploading {local_file_path} to {remote_file_path}...")
#     sftp.put(local_file_path, remote_file_path)
#     print("File uploaded successfully!")

#     # # Close the SFTP session and SSH connection
#     sftp.close()
#     ssh_client.close()
#     print("Connection closed.")

# except Exception as e:
#     print(f"An error occurred: {e}")

import subprocess
import tempfile
import os
import base64

def transfer_file_via_scp(page_name, page_version, file_data):
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
        target_file = f"{page_name}_{page_version}.php"
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
