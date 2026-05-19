import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER     = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM    = os.getenv("EMAIL_FROM", SMTP_USER)


def _send_email(to_email: str, subject: str, html_body: str) -> bool:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"Sport Events <{EMAIL_FROM}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, to_email, msg.as_string())
        print(f"[Email] Sent to {to_email}")
        return True
    except Exception as exc:
        print(f"[Email ERROR] {exc}")
        return False


def _base_template(inner_html: str, title: str = "Sport Events") -> str:
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;background-color:#0D1117;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0D1117;padding:48px 16px;">
    <tr>
      <td align="center">
        <table width="520" cellpadding="0" cellspacing="0"
          style="background:linear-gradient(160deg,#161B22 0%,#1A2236 100%);
                 border:1px solid rgba(255,255,255,0.08);border-radius:20px;overflow:hidden;
                 box-shadow:0 24px 80px rgba(0,0,0,0.6);">

          <tr>
            <td style="background:linear-gradient(135deg,#1F6BFF 0%,#0041CC 100%);padding:36px 40px;text-align:center;">
              <div style="font-size:40px;line-height:1;margin-bottom:10px;">🏆</div>
              <h1 style="margin:0;color:#ffffff;font-size:22px;font-weight:700;letter-spacing:-0.3px;">
                Sport Events
              </h1>
              <p style="margin:6px 0 0;color:rgba(255,255,255,0.7);font-size:13px;">
                Gestion d'événements sportifs
              </p>
            </td>
          </tr>

          <tr>
            <td style="padding:40px 40px 32px;">
              {inner_html}
            </td>
          </tr>

          <tr>
            <td style="background:rgba(0,0,0,0.2);padding:18px 40px;
                       border-top:1px solid rgba(255,255,255,0.05);text-align:center;">
              <p style="margin:0;color:#30363D;font-size:12px;">
                © 2026 Sport Events · Tous droits réservés
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def send_otp_email(to_email: str, display_name: str, otp: str) -> bool:
    otp_display = otp
    inner = f"""
    <p style="margin:0 0 6px;color:#8B949E;font-size:15px;">
      Bonjour, <strong style="color:#F0F6FC;">{display_name}</strong> 👋
    </p>
    <p style="margin:0 0 32px;color:#8B949E;font-size:15px;line-height:1.6;">
      Utilisez ce code pour vérifier votre compte. Il est valable <strong style="color:#F0F6FC;">10 minutes</strong>.
    </p>
    <div style="background:rgba(31,107,255,0.08);border:2px solid rgba(31,107,255,0.35);
                border-radius:16px;padding:28px 24px;text-align:center;margin-bottom:28px;">
      <div style="font-size:52px;font-weight:800;color:#4D8EFF;
                  letter-spacing:16px;font-family:'Courier New',monospace;line-height:1;">
        {otp_display}
      </div>
      <p style="margin:14px 0 0;color:#484F58;font-size:12px;text-transform:uppercase;letter-spacing:1px;">
        Code de vérification à 6 chiffres
      </p>
    </div>
    <p style="color:#484F58;font-size:13px;margin:0;line-height:1.7;
              border-top:1px solid rgba(255,255,255,0.06);padding-top:24px;">
      🔒 Ne partagez jamais ce code.<br>
      Si vous n'avez pas créé de compte, ignorez cet email.
    </p>"""

    html = _base_template(inner, "Code de vérification")
    return _send_email(to_email, f"🏆 {otp_display} – Votre code de vérification Sport Events", html)


def send_team_assignment_email(to_email: str, player_name: str, team_name: str, sport: str) -> bool:
    inner = f"""
    <p style="margin:0 0 6px;color:#8B949E;font-size:15px;">
      Bonjour, <strong style="color:#F0F6FC;">{player_name}</strong> 👋
    </p>
    <p style="margin:0 0 28px;color:#8B949E;font-size:15px;line-height:1.6;">
      Vous avez été ajouté à une équipe !
    </p>
    <div style="background:rgba(16,185,129,0.08);border:2px solid rgba(16,185,129,0.35);
                border-radius:16px;padding:28px 24px;text-align:center;margin-bottom:28px;">
      <div style="font-size:36px;margin-bottom:12px;">⚽</div>
      <div style="font-size:24px;font-weight:800;color:#56D364;line-height:1;margin-bottom:8px;">
        {team_name}
      </div>
      <p style="margin:0;color:#8B949E;font-size:14px;">Sport : <strong style="color:#F0F6FC;">{sport}</strong></p>
    </div>
    <p style="color:#484F58;font-size:13px;margin:0;line-height:1.7;
              border-top:1px solid rgba(255,255,255,0.06);padding-top:24px;">
      Connectez-vous à votre compte Sport Events pour voir les détails de votre équipe et les matchs à venir.
    </p>"""

    html = _base_template(inner, "Assignation Équipe")
    return _send_email(to_email, f"⚽ Vous avez été ajouté à l'équipe {team_name}", html)


def send_event_notification_email(to_email: str, display_name: str, event_title: str, sport: str, event_date: str, location: str) -> bool:
    inner = f"""
    <p style="margin:0 0 6px;color:#8B949E;font-size:15px;">
      Bonjour, <strong style="color:#F0F6FC;">{display_name}</strong> 👋
    </p>
    <p style="margin:0 0 28px;color:#8B949E;font-size:15px;line-height:1.6;">
      Un nouvel événement de <strong style="color:#4D8EFF;">{sport}</strong> a été publié !
    </p>
    <div style="background:rgba(31,107,255,0.08);border:2px solid rgba(31,107,255,0.35);
                border-radius:16px;padding:28px 24px;margin-bottom:28px;">
      <div style="font-size:20px;font-weight:800;color:#F0F6FC;margin-bottom:12px;">{event_title}</div>
      <p style="margin:0 0 8px;color:#8B949E;font-size:14px;">📍 {location or 'Lieu non défini'}</p>
      <p style="margin:0;color:#8B949E;font-size:14px;">📅 {event_date or 'Date non définie'}</p>
    </div>
    <p style="color:#484F58;font-size:13px;margin:0;line-height:1.7;
              border-top:1px solid rgba(255,255,255,0.06);padding-top:24px;">
      Connectez-vous pour plus de détails et réserver votre place !
    </p>"""

    html = _base_template(inner, "Nouvel Événement")
    return _send_email(to_email, f"🏆 Nouvel événement {sport} : {event_title}", html)


def send_booking_confirmation_email(to_email: str, display_name: str, match_info: str, qr_code_url: str) -> bool:
    inner = f"""
    <p style="margin:0 0 6px;color:#8B949E;font-size:15px;">
      Bonjour, <strong style="color:#F0F6FC;">{display_name}</strong> 👋
    </p>
    <p style="margin:0 0 28px;color:#8B949E;font-size:15px;line-height:1.6;">
      Votre réservation est confirmée !
    </p>
    <div style="background:rgba(16,185,129,0.08);border:2px solid rgba(16,185,129,0.35);
                border-radius:16px;padding:28px 24px;text-align:center;margin-bottom:28px;">
      <div style="font-size:36px;margin-bottom:12px;">🎟️</div>
      <div style="font-size:18px;font-weight:700;color:#56D364;margin-bottom:16px;">{match_info}</div>
      <img src="{qr_code_url}" alt="QR Code" style="width:200px;height:200px;border-radius:12px;border:2px solid rgba(255,255,255,0.1);">
      <p style="margin:14px 0 0;color:#484F58;font-size:12px;">Présentez ce QR code à l'entrée du match</p>
    </div>"""

    html = _base_template(inner, "Confirmation Réservation")
    return _send_email(to_email, f"🎟️ Réservation confirmée – {match_info}", html)
