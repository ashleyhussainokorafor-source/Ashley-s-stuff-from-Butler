#!/usr/bin/env python3
"""
Transmits Batch 1 university faculty applications via Gmail API with Dr. Ashley's CV attached.
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

BATCH_1_TARGETS = [
    {
        "to": "job@nottingham.edu.cn",
        "name": "University of Nottingham Ningbo China (UNNC)",
        "subject": "Academic Faculty Application: Healthcare Administration & Management — Dr. Ashley Hussain-Okorafor, DBA, MHA",
        "body": """Dear Members of the Faculty Search Committee and Dean of Nottingham University Business School,

I am writing to submit my formal application for a faculty position in Healthcare Administration, Health Management, and Strategic Leadership at the University of Nottingham Ningbo China for the upcoming academic term. As a scholar-practitioner holding an accredited Doctor of Business Administration (DBA) with a concentration in Health Administration and a Master of Science in Health Administration (MHA), combined with over six years of full-time lecturing experience in the California State University system (CSUSB), I am prepared to deliver rigorous, student-centered instruction within UNNC's distinguished international academic environment.

Throughout my six-year tenure as a full-time university lecturer at California State University, San Bernardino, I instructed diverse undergraduate and graduate cohorts in healthcare delivery systems, health informatics, and organizational change theory. In my current capacity as Director of Student Support Services and Adjunct Professor at Charisma University, I govern academic retention frameworks and virtual seminars for international students. 

My doctoral research, titled "Malpractice Lawsuits Involving Nurses in the Workplace: Examining Legal Implications and Administrative Strategies to Mitigate Risk Within Healthcare Systems," bridges clinical risk mitigation with institutional governance. Furthermore, I have had the honor of presenting peer-reviewed research internationally at the International Conference of Education, Research, and Innovation (ICERI) in Seville, Spain.

I am prepared for relocation by January 1, 2027, alongside my spouse—who is an experienced US Registered Nurse specializing in oncology and infusion therapy—and our two dependent minor children. Under the State Administration of Foreign Experts Affairs (SAFEA) criteria, my doctorate and university tenure qualify me for expedited Category A/B Foreign Expert Work Permit and Z-visa sponsorship.

Attached please find my complete Curriculum Vitae. I welcome the opportunity to discuss how my academic background and commitment to cross-cultural education can contribute to UNNC.

Sincerely,

Dr. Ashley Hussain-Okorafor, DBA, MHA
Former Full-Time Lecturer, California State University, San Bernardino
Email: ashleyhussainokorafor@gmail.com | Phone/WhatsApp: +1 (951) 445-5799
LinkedIn: https://www.linkedin.com/in/dr-ashley-hussain-okorafor-dba-mha-03032b40/"""
    },
    {
        "to": "hiring@wku.edu.cn",
        "name": "Wenzhou-Kean University (WKU)",
        "subject": "Faculty Position Application: Management & Health Administration — Dr. Ashley Hussain-Okorafor, DBA, MHA",
        "body": """Dear Members of the Search Committee and Dean of the College of Business and Public Management,

I am writing to express my strong candidacy for a faculty appointment in Management, Health Administration, or Organizational Behavior at Wenzhou-Kean University. With an accredited Doctor of Business Administration (DBA), a Master of Science in Health Administration (MHA), and six years of experience as a full-time university lecturer at California State University, San Bernardino (CSUSB), I offer a proven track record of delivering US-accredited, interactive business and management curriculum.

As an American educator with deep roots in public university instruction, I specialize in active-learning pedagogies, Harvard-style case studies, and empirical research mentoring. My doctoral dissertation examined clinical risk mitigation and administrative governance within complex hospital environments, and I have presented scholarly work at the ICERI conference in Seville, Spain.

Wenzhou-Kean's unique mission of bridging American and Chinese higher education resonates strongly with my experience teaching multicultural student populations. My family and I are prepared to deploy to Wenzhou by January 1, 2027 (in advance of the Spring 2027 semester). My credentials meet the State Administration of Foreign Experts Affairs (SAFEA) Category A/B Foreign Expert tier, facilitating streamlined Z-visa and dependent S1 visa issuance.

My Curriculum Vitae is attached for your review. I look forward to the possibility of discussing how I can support WKU's academic mission.

Respectfully,

Dr. Ashley Hussain-Okorafor, DBA, MHA
Email: ashleyhussainokorafor@gmail.com | WhatsApp: +1 (951) 445-5799"""
    },
    {
        "to": "recruitment@dukekunshan.edu.cn",
        "name": "Duke Kunshan University (DKU)",
        "subject": "Academic Faculty Application: Global Health & Healthcare Administration — Dr. Ashley Hussain-Okorafor, DBA, MHA",
        "body": """Dear Members of the Faculty Search Committee,

I am writing to submit my application for an instructional faculty appointment in Global Health, Healthcare Management, or Organizational Systems at Duke Kunshan University. As a scholar holding a Doctor of Business Administration (DBA) in Health Administration and an MHA, with six years of full-time lecturing tenure at California State University, San Bernardino (CSUSB), I am dedicated to cultivating critical thinking, interdisciplinary inquiry, and operational acumen in undergraduate cohorts.

My instructional background encompasses healthcare delivery systems, operational change theory, and healthcare risk governance. My doctoral dissertation analyzed legal implications and administrative strategies to mitigate risk within healthcare institutions, and my scholarship has been presented at international forums including ICERI in Seville, Spain.

DKU's commitment to liberal arts excellence and global health leadership provides an ideal institutional home for my academic values. I am available for relocation by January 1, 2027, with my spouse (an oncology RN) and our two children. Under Chinese labor regulations, my doctorate and university lecturing background qualify me as a Category A/B Foreign Expert for expedited visa processing.

Please find my full CV attached. I would be honored to speak with your search committee regarding instructional opportunities.

Sincerely,

Dr. Ashley Hussain-Okorafor, DBA, MHA
Email: ashleyhussainokorafor@gmail.com | Phone: +1 (951) 445-5799"""
    },
    {
        "to": "recruitment@uic.edu.cn",
        "name": "BNU-HKBU United International College (UIC)",
        "subject": "Faculty Application: Healthcare Management & Business Administration — Dr. Ashley Hussain-Okorafor, DBA, MHA",
        "body": """Dear Search Committee Members and Dean of the Faculty of Business and Management,

I am pleased to apply for a faculty position in Management, Healthcare Administration, or Organizational Theory at BNU-HKBU United International College for the upcoming academic term. As an American academic holding a Doctor of Business Administration (DBA) and an MHA, with over a decade of teaching and higher-education administration experience—including six years as a full-time university lecturer at California State University, San Bernardino—I am prepared to contribute immediately to UIC’s English-medium collegiate environment.

Throughout my career, I have focused on preparing students for impactful leadership in complex operational environments, integrating rigorous case analysis, healthcare informatics, and ethical governance. My doctoral research investigated nurse malpractice risk mitigation and healthcare leadership strategies, and I have presented scholarly work at international academic conferences.

Located in the dynamic Greater Bay Area, UIC represents an exceptional platform for cross-cultural higher education. My family is prepared for relocation to Zhuhai by January 1, 2027. My accredited doctoral credentials qualify for Category A/B Foreign Expert work authorization.

Attached is my CV for your evaluation. I would welcome the opportunity to connect for an interview at your convenience.

Kind regards,

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
    for t in BATCH_1_TARGETS:
        print(f"Sending faculty application to {t['name']} ({t['to']})...")
        try:
            msg_id = send_application(t)
            print(f"  -> SUCCESS! Sent message ID: {msg_id}")
        except Exception as e:
            print(f"  -> ERROR sending to {t['to']}: {e}")
