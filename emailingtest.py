import os
import smtplib
from email.message import EmailMessage

# Configuration
SENDER_EMAIL = os.environ.get("GMAIL_USER", "theoliverhakansson@gmail.com")
APP_PASSWORD = os.environ.get("GMAIL_APP_PASS", "hbtc sbnq qdkv atll")

def send_experiment_email(recipient_email, html_body, txt_content, png_attachment_path):
    """
    Send an email with HTML body and two attachments (txt and png)
    
    Args:
        recipient_email (str): Email address to send to
        html_body (str): HTML content for the email body
        txt_content (str): Content to attach as .txt file
        png_attachment_path (str): Path to .png file to attach
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    
    try:
        # Initialize Message
        msg = EmailMessage()
        msg["Subject"] = "Experiment Report from Current Monitoring"
        msg["From"] = SENDER_EMAIL
        msg["To"] = recipient_email
        
        # Add plain text fallback
        msg.set_content("Please enable HTML to view this report.")
        
        # Add HTML version
        msg.add_alternative(html_body, subtype="html")
        
        # Attach txt content as file
        msg.add_attachment(
            txt_content,
            filename="experiment_data.txt"
        )
        print("Attached: experiment_data.txt")
        
        # Attach .png file if it exists
        if os.path.exists(png_attachment_path):
            with open(png_attachment_path, "rb") as file:
                file_data = file.read()
                file_name = os.path.basename(png_attachment_path)
            
            msg.add_attachment(
                file_data,
                maintype="image",
                subtype="png",
                filename=file_name
            )
            print(f"Attached: {file_name}")
        else:
            print(f"Warning: PNG file '{png_attachment_path}' not found.")
        
        # Send email
        print("Connecting to Gmail SMTP...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)
        
        print(f"🎉 Email successfully sent to {recipient_email}!")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ Error: Authentication failed. Check your email and App Password.")
        return False
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return False