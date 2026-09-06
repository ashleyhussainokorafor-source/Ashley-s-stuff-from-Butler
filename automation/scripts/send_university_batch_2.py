#!/usr/bin/env python3
"""
Executes university faculty applications via Gmail API with Dr. Ashley's CV attached.
"""

import json
import base64
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH = "/data/google_token.json"
CV_PATH = "/data/personal/relocation-china/Dr_Ashley_Hussain_Okorafor_China_Academic_CV.docx"

with open(TOKEN_PATH, "r") as f:
    token_data = json.load(f)

creds = Credentials(
    token=token_data.get("token"),
    refresh_token=token_data.get("refresh_token"),
    token_uri=token_data.get("token_uri"),
    client_id=token_data.get("client_id"),
    client_secret="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"
)

service = build("gmail", "v1", credentials=creds)

BATCH_2_TARGETS = [
    {
        "to": "talents-sme@cuhk.edu.cn",
        "name": "CUHK Shenzhen (School of Management and Economics)",
        "subject": "Faculty Application: Management & Healthcare Administration — Dr. Ashley Hussain-Okorafor, DBA, MHA",
        "body": """Dear Members of the Faculty Search Committee and Dean of the School of Management and Economics,

I am writing to express my strong interest in joining the faculty at the Chinese University of Hong Kong, Shenzhen (CUHK-Shenzhen). As an academic scholar holding an accredited Doctor of Business Administration (DBA) with a concentration in Health Administration and a Master of Science in Health Administration (MHA), combined with six years of full-time lecturing experience in the California State University system (CSUSB), I am prepared to deliver rigorous, student-centered instruction in healthcare management, organizational behavior, and global strategic leadership.

Throughout my six years as a full-time university lecturer at California State University, San Bernardino, I taught diverse undergraduate and graduate cohorts in healthcare delivery systems, health informatics, and operational change theory. In my current capacity as Director of Student Support Services and Adjunct Professor at Charisma University, I govern academic retention frameworks and virtual seminars for international students.

My doctoral research, titled "Malpractice Lawsuits Involving Nurses in the Workplace: Examining Legal Implications and Administrative Strategies to Mitigate Risk Within Healthcare Systems," bridges clinical risk mitigation with institutional governance. Furthermore, I have had the honor of presenting peer-reviewed research internationally at the International Conference of Education, Research, and Innovation (ICERI) in Seville, Spain.

CUHK-Shenzhen's rapid ascent and dedication to international scholarship in the Greater Bay Area provide an ideal environment for my teaching and research. I am prepared for relocation by January 1, 2027, alongside my spouse—who is an experienced US Registered Nurse specializing in oncology and infusion therapy—and our two dependent minor children. Under the State Administration of Foreign Experts Affairs (SAFEA) framework, my doctorate and university tenure qualify me for expedited Category A/B Foreign Expert Work Permit and Z-visa sponsorship.

Attached please find my complete Curriculum Vitae. I welcome the opportunity to discuss how my academic background can contribute to the continued excellence of CUHK-Shenzhen.

Sincerely,

Dr. Ashley Hussain-Okorafor, DBA, MHA
Former Full-Time Lecturer, California State University, San Bernardino
Email: ashleyhussainokorafor@gmail.com | Phone/WhatsApp: +1 (951) 445-5799
LinkedIn: https://www.linkedin.com/in/dr-ashley-hussain-okorafor-dba-mha-03032b40/"""
    },
    {
        "to": "szuhr@szu.edu.cn",
        "name": "Shenzhen University (College of Management)",
        "subject": "Academic Faculty Application: Health Management & Public Administration — Dr. Ashley Hussain-Okorafor, DBA, MHA",
        "body": """Dear Members of the Search Committee and Dean of the College of Management,

I am pleased to submit my application for an instructional faculty appointment in Healthcare Management, Public Administration, or Organizational Systems at Shenzhen University. Holding an accredited Doctor of Business Administration (DBA) and an MHA, with six years of full-time lecturing tenure at California State University, San Bernardino (CSUSB), I offer a demonstrated track record of delivering high-impact, case-based management education.

My academic focus centers on healthcare delivery systems, operational change theory, and institutional risk management. My doctoral dissertation analyzed administrative strategies to mitigate legal and operational risk within healthcare institutions, and my scholarship has been presented at international forums including ICERI in Seville, Spain.

As Shenzhen continues to lead innovation and international education in southern China, I would be honored to contribute to SZU's dynamic global faculty. My family is prepared for relocation to Shenzhen by January 1, 2027. My accredited doctoral credentials qualify for Category A/B Foreign Expert work authorization and Z-visa issuance for myself and S1 dependent visas for my family.

Attached is my CV for your evaluation. I look forward to the possibility of discussing how I can support SZU's academic mission.

Respectfully,

Dr. Ashley Hussain-Okorafor, DBA, MHA
Email: ashleyhussainokorafor@gmail.com | WhatsApp: +1 (951) 445-5799"""
    },
    {
        "to": "rsc@ouc.edu.cn",
        "name": "Ocean University of China (School of Management)",
        "subject": "Faculty Application: Healthcare Administration & Business Management — Dr. Ashley Hussain-Okorafor, DBA, MHA",
        "body": """Dear Members of the Faculty Search Committee,

I am writing to submit my formal application for a faculty position in Management, Healthcare Administration, or Organizational Behavior at Ocean University of China for the upcoming academic term. As an American academic holding a Doctor of Business Administration (DBA) and an MHA, with over a decade of teaching and higher-education administration experience—including six years as a full-time university lecturer at California State University, San Bernardino—I am prepared to contribute immediately to OUC’s collegiate programs.

Throughout my career, I have specialized in equipping students with practical analytical frameworks to solve complex operational challenges. My doctoral dissertation examined clinical risk mitigation and administrative governance within healthcare systems, and I have presented scholarly work at international academic conferences.

Qingdao’s rich coastal culture and OUC’s prestigious academic standing offer an ideal community for my family and professional career. We are prepared for relocation by January 1, 2027. My doctorate and university lecturing background qualify me as a Category A/B Foreign Expert for expedited visa processing.

Attached please find my complete CV. I would welcome the privilege of connecting via Zoom to discuss instructional opportunities.

Sincerely,

Dr. Ashley Hussain-Okorafor, DBA, MHA
Email: ashleyhussainokorafor@gmail.com | Phone: +1 (951) 445-5799"""
    },
    {
        "to": "qduhr@qdu.edu.cn",
        "name": "Qingdao University (Business School)",
        "subject": "Faculty Position Application: Health Administration & Strategic Management — Dr. Ashley Hussain-Okorafor, DBA, MHA",
        "body": """Dear Search Committee Members and Dean of the Business School,

I am writing to express my strong candidacy for a faculty appointment in Healthcare Administration, Health Policy, or Organizational Leadership at Qingdao University. With an accredited Doctor of Business Administration (DBA), an MHA, and six years of full-time lecturing experience at California State University, San Bernardino (CSUSB), I bring seasoned pedagogical expertise in bridging Western healthcare management models with global health challenges.

My research and teaching emphasize operational efficiency, clinical risk mitigation, and institutional leadership. My doctoral research investigated nurse malpractice litigation and risk management strategies in hospital systems, and my scholarship was featured at the 11th Annual ICERI conference in Seville, Spain.

My family and I are committed to relocating to Qingdao by January 1, 2027, and I am available for immediate engagement for the Spring 2027 semester. My credentials qualify for expedited Category A/B Foreign Expert visa clearance, with accompanying S1 dependent visas for my spouse (an oncology RN) and our two children.

Please find my CV attached for your review. I look forward to the opportunity to speak with your academic leadership team.

Warm regards,

Dr. Ashley Hussain-Okorafor, DBA, MHA
Email: ashleyhussainokorafor@gmail.com | Phone/WhatsApp: +1 (951) 445-5799"""
    }
]

def send_application(target):
    msg = MIMEMultipart()
    msg["to"] = target["to"]
    msg["from"] = "ashleyhussainokorafor@gmail.com"
    msg["subject"] = target["subject"]

    msg.attach(MIMEText(target["body"], "plain"))

    # Attach CV
    if os.path.exists(CV_PATH):
        with open(CV_PATH, "rb") as f:
            part = MIMEBase("application", "vnd.openxmlformats-officedocument.wordprocessingml.document")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename=Dr_Ashley_Hussain_Okorafor_China_Academic_CV.docx"
            )
            msg.attach(part)

    raw_msg = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    sent = service.users().messages().send(userId="me", body={"raw": raw_msg}).execute()
    return sent.get("id")

if __name__ == "__main__":
    for t in BATCH_2_TARGETS:
        print(f"Sending faculty application to {t['name']} ({t['to']})...")
        try:
            msg_id = send_application(t)
            print(f"  -> SUCCESS! Sent message ID: {msg_id}")
        except Exception as e:
            print(f"  -> ERROR sending to {t['to']}: {e}")
