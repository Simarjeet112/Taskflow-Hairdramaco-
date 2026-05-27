import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email: str, subject: str, body: str):
    try:
        sender_email = os.getenv("GMAIL_USER")
        sender_password = os.getenv("GMAIL_APP_PASSWORD")

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = to_email

        html_part = MIMEText(body, "html")
        msg.attach(html_part)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
            print(f"[EMAIL] Sent to {to_email}: {subject}")
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")

def send_task_assigned_email(to_email: str, to_name: str, task_title: str, creator_name: str):
    subject = f"New task assigned to you — {task_title}"
    body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2563eb;">TaskFlow — New Task Assigned</h2>
        <p>Hi <strong>{to_name}</strong>,</p>
        <p>You have been assigned a new task by <strong>{creator_name}</strong>.</p>
        <div style="background: #f3f4f6; padding: 16px; border-radius: 8px; margin: 16px 0;">
            <h3 style="margin: 0; color: #111827;">📋 {task_title}</h3>
        </div>
        <p>Log in to TaskFlow to view and manage your task.</p>
        <p style="color: #6b7280; font-size: 14px;">— Team TaskFlow</p>
    </div>
    """
    send_email(to_email, subject, body)

def send_task_completed_email(to_email: str, to_name: str, task_title: str):
    subject = f"Task completed — {task_title}"
    body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #16a34a;">TaskFlow — Task Completed ✅</h2>
        <p>Hi <strong>{to_name}</strong>,</p>
        <p>Great news! Your task has been marked as completed.</p>
        <div style="background: #f0fdf4; padding: 16px; border-radius: 8px; margin: 16px 0;">
            <h3 style="margin: 0; color: #15803d;">✅ {task_title}</h3>
        </div>
        <p>Log in to TaskFlow to view all your tasks.</p>
        <p style="color: #6b7280; font-size: 14px;">— Team TaskFlow</p>
    </div>
    """
    send_email(to_email, subject, body)