from ftplib import FTP
import os
import base64
import traceback

def push_changes_to_ftp(page_name, page_version, last_updated, user_id,user_name, file_data,
                        ftp_host="bacancy-Vostro-3508", ftp_user="khushbu", ftp_pass="khushbu",
                        target_dir="/home/bacancy/Desktop/automated_seo/temp"):
    try:
        # Initialize FTP connection
        ftp = FTP('bacancy-Vostro-3580', timeout=10)
        ftp.login('khushbu', 'khushbu')

        print("Connected to FTP server successfully.")

        target_file = f"{page_name}_{page_version}.php"
        target_file_path = os.path.join(target_dir, target_file)

        ftp.retrlines("LIST")

        # Decode and write the binary data to a local file
        if file_data:
            try:
                decoded_data = None
                if isinstance(file_data, bytes):
                    decoded_data = base64.b64decode(file_data)

                if decoded_data:
                    with open(target_file_path, 'wb') as file:
                        file.write(decoded_data)
                    print(f"Decoded and saved file to {target_file_path}")
                else:
                    return False
            except Exception as e:
                print(f"Error writing file: {str(e)}")
                return False

        # Upload the file to FTP server
        with open(target_file_path, 'rb') as file:
            ftp.storbinary(f"STOR {target_file}", file)
        print(f"Uploaded {target_file} to FTP server.")

        commit_message = (f"Page Update: {page_name}\n"
                          f"Version: {page_version}\n"
                          f"Last Updated: {last_updated}\n"
                          f"User ID: {user_id}\n"
                          f"User Name: {user_name}\n")

        print(f"Changes uploaded with the following message:\n{commit_message}")

        ftp.quit()
        print(f"Successfully closed the FTP connection.")

        return True
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        traceback.print_exc()
        return False







