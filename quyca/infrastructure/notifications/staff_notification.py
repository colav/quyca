from typing import Any, cast
from infrastructure.repositories.gmail_repository import GmailRepository
from infrastructure.email_templates.staff_report_templates import build_email_template
from domain.models.staff_report_model import StaffReport


class StaffNotification:
    """
    Injects Gmail repository dependency.
    """

    def __init__(self, gmail_repo: GmailRepository):
        self.gmail_repo: GmailRepository = gmail_repo

    """
    Chooses template (accepted/warnings/rejected) and sends email with attachments.
    """

    def send_report(
        self,
        staff_report: StaffReport,
        institution: str,
        filename: str,
        upload_date: str,
        user: str,
        email: str,
        file_type: str,
        attachments: list[dict],
        ror_id: str,
    ) -> dict[str, Any]:
        tipo_correo = (
            "rechazado"
            if staff_report.total_errores > 0
            else ("advertencias" if len(staff_report.advertencias) > 0 else "aceptado")
        )

        subject, body_html = build_email_template(
            tipo=tipo_correo, rol=user, institution=institution, filename=filename, upload_date=upload_date
        )

        return self.gmail_repo.send_labeled_email(
            to_email=email,
            subject=subject,
            body_html=body_html,
            attachments=attachments,
            institution=institution,
            tipo=file_type,
            ror_id=ror_id,
        )

    def send_custom_email(
        self, subject: str, rol: str, institution: str, email: str, password: str, ror_id: str
    ) -> dict:
        """
        Sends a plain custom email — used for user account notifications.
        """

        body_html = f"""
            <html>
                <body style='font-family: Arial, sans-serif; line-height: 1.6;'>
                    <p>Estimado(a) <b>{rol}</b> – {institution},</p>
                    <p>Nos complace informarte que tu cuenta ha sido creada exitosamente en <b><span style="color:#39658c;">Impact</span><span style="color:#f6a611;">U</span></b></p>
                    <p>Podrás acceder al módulo de <b>carga de datos institucionales</b> a través del siguiente enlace:</p>
                    <p><a href=https://impactu.colav.co/submit>https://impactu.colav.co/submit</p>
                    <p><b>Datos de acceso:</b></p>
                    <ul>
                        <li><p>Usuario: {email}</p></li>
                        <li><p>Contraseña: {password}</p></li>
                    </ul>
                    <p>Como encargado de <b>suministrar y garantizar la calidad de los datos institucionales</b>, te\n
                    invitamos a consultar la siguiente guía antes de realizar tu primera carga:\n</p>
                    <p><a href=https://data.colav.co/Formato_datos_impactu.pdf>https://data.colav.co/Formato_datos_impactu.pdf</p>
                    <p>Este documento detalla los formatos requeridos y las especificaciones necesarias para\n
                    garantizar la correcta integración de los datos en la plataforma.</p>
                    <p>Si tienes preguntas o necesitas soporte técnico, puedes escribirnos a\n
                    <strong>grupocolav@udea.edu.co</strong></p>
                    <p>Gracias por tu compromiso con la calidad de los datos y por contribuir al fortalecimiento del\n
                    ecosistema de información científica de <b><span style="color:#39658c;">Impact</span><span style="color:#f6a611;">U</span></b></p>
                    <p>Atentamente,</p>
                    <p><b>Equipo <span style="color:#39658c;">Impact</span><span style="color:#f6a611;">U</span></b></p>
                    <br><br>
                    <em>Este es un mensaje automático. No responda a este correo.</em>
                </body>
            </html>
            """

        return self.gmail_repo.send_labeled_email(
            to_email=email,
            subject=subject,
            body_html=body_html,
            attachments=[],
            institution=institution,
            tipo="Usuarios",
            ror_id=ror_id,
        )

    def send_email_change_password(
        self, email: str, subject: str, password: str, institution: str, ror_id: str
    ) -> dict:
        """
        Send a simple email — used for password change notifications.
        """
        body_html = f"""
        <html>
            <body>
                <p><b><span style="color:#39658c;">Impact</span><span style="color:#f6a611;">U</span></b> te informa que tu contraseña ha sido restablecida por el administrador.</p>
                <p>Nueva contraseña: {password}</P>
                <p>Si tienes preguntas o necesitas soporte técnico, puedes escribirnos a\n
                <strong>grupocolav@udea.edu.co</strong></p>
                <p>Atentamente,</p>
                <p><b>Equipo <span style="color:#39658c;">Impact</span><span style="color:#f6a611;">U</span></b></p>
                <br><br>
                <em>Este es un mensaje automático. No responda a este correo.</em>
            </body>
        </html>
        """

        return self.gmail_repo.send_labeled_email(
            to_email=email,
            subject=subject,
            body_html=body_html,
            attachments=[],
            institution=institution,
            tipo="Usuarios",
            ror_id=ror_id,
        )
