import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

def create_pdf(filename, title, content_blocks):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    doc = SimpleDocTemplate(filename, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=12
    )
    
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0F766E'),
        spaceBefore=10,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )
    
    speaker_style = ParagraphStyle(
        'SpeakerText',
        parent=styles['BodyText'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1D4ED8'),
        spaceBefore=4,
        spaceAfter=2
    )
    
    story = [Paragraph(title, title_style), HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0F766E'), spaceAfter=15)]
    
    for block in content_blocks:
        b_type = block.get('type', 'p')
        text = block.get('text', '')
        if b_type == 'h2':
            story.append(Paragraph(text, heading_style))
        elif b_type == 'speaker':
            story.append(Paragraph(text, speaker_style))
        elif b_type == 'p':
            story.append(Paragraph(text, body_style))
        elif b_type == 'spacer':
            story.append(Spacer(1, block.get('height', 10)))
            
    doc.build(story)
    print(f"Generated PDF: {filename}")

def generate_all_pdfs():
    output_dir = "data"
    
    # 1. Job Description PDF
    jd_blocks = [
        {"type": "h2", "text": "AI Engineer — Agentic Systems (Freight Operations)"},
        {"type": "p", "text": "<b>Company:</b> Cargonet AI — a freight-tech company that runs AI 'agent' systems in real production, handling shipment quoting, booking, tracking, document processing, and fixing errors automatically."},
        {"type": "h2", "text": "About the Role"},
        {"type": "p", "text": "We need an engineer to help improve our existing AI agent system (planner, executor, reviewer, and specialized agents working together). This is not a research-only job. You will build real features that go live for real users, mostly by directing AI coding tools (like Claude Code) rather than writing every line by hand — and you'll be responsible for fixing things when they break in production."},
        {"type": "h2", "text": "What You'll Do"},
        {"type": "p", "text": "• Improve the multi-agent AI system powering freight ops (quoting, booking, tracking, OCR document processing, error handling)."},
        {"type": "p", "text": "• Build features mainly by directing AI coding tools (like Claude Code) — reviewing and guiding their output, not just writing code yourself."},
        {"type": "p", "text": "• Work on the Python backend (microservices) and React.js front-end, using MongoDB to build clean operator interfaces."},
        {"type": "p", "text": "• Improve prompting, tools/memory access, RAG / vector search, and model selection (balancing quality vs cost)."},
        {"type": "p", "text": "• Keep the live system running smoothly — find and fix bugs when an AI agent misbehaves, taking full ownership in production."},
        {"type": "p", "text": "• Connect system to external carrier APIs, business software, and OCR document scanning for invoices and BOLs."},
        {"type": "h2", "text": "What We're Looking For"},
        {"type": "p", "text": "• Solid Python backend skills (building REST APIs, microservices)."},
        {"type": "p", "text": "• Real hands-on experience with AI/LLM systems (prompt engineering, RAG/vector search, evaluation)."},
        {"type": "p", "text": "• Comfortable taking ownership when something breaks in production."},
        {"type": "p", "text": "• Basic React.js skills for building simple front-end screens."},
        {"type": "p", "text": "• Nice to have: experience with logistics/freight, document scanning (OCR), or system integrations."}
    ]
    create_pdf(os.path.join(output_dir, "02_Job_Description.pdf"), "Cargonet AI — Job Description", jd_blocks)
    
    # 2. Resume A: Rohan Malhotra
    resume_a_blocks = [
        {"type": "h2", "text": "Rohan Malhotra — Senior AI/Backend Engineer"},
        {"type": "p", "text": "<b>Email:</b> rohan.malhotra@techmail.com | <b>Phone:</b> +1 (555) 019-2834"},
        {"type": "h2", "text": "Summary"},
        {"type": "p", "text": "AI engineer with 3.5 years of experience building multi-agent LLM systems and Python backends. Led design of a production agent platform now handling thousands of daily freight exceptions. Known for moving fast and shipping under pressure."},
        {"type": "h2", "text": "Work Experience"},
        {"type": "p", "text": "<b>Senior AI Engineer — Voltrix Logistics Tech</b> (Jan 2025 – Present, 7 months)"},
        {"type": "p", "text": "• Designed and built the exception-handling engine end-to-end for Voltrix's multi-agent freight ops platform (planner/executor/reviewer pattern), cutting manual exception review time by 40%."},
        {"type": "p", "text": "• Owned prompt design and model routing across GPT-4 and open-weight SLMs, reducing inference cost by ~30%."},
        {"type": "p", "text": "• Sole architect of the retry/escalation logic now running in production, handling 5,000+ freight exceptions/month."},
        {"type": "p", "text": "• Presented the system design at a company-wide tech talk."},
        {"type": "p", "text": "<b>AI Engineer — Quickship Data Systems</b> (Feb 2024 – Dec 2024, 11 months)"},
        {"type": "p", "text": "• Built a RAG pipeline over carrier rate documents using LangChain + Pinecone, cutting manual rate lookup time significantly."},
        {"type": "p", "text": "• Improved BOL/invoice extraction accuracy through better OCR pre-processing."},
        {"type": "p", "text": "<b>Backend Developer — Nimbus Cloud Solutions</b> (Aug 2022 – Jan 2024, 1.5 years)"},
        {"type": "p", "text": "• Built Python microservices for a SaaS analytics product used by 50+ enterprise clients."},
        {"type": "p", "text": "• Led a 4-person team migrating a legacy monolith to microservices."},
        {"type": "h2", "text": "Skills"},
        {"type": "p", "text": "Python, FastAPI, LangGraph, CrewAI, MongoDB, React (basic), RAG, Vector Search (Pinecone, FAISS), Prompt Engineering, Docker, Kubernetes."},
        {"type": "h2", "text": "Education & Certifications"},
        {"type": "p", "text": "B.Tech Computer Science, 2022 | LangChain for LLM Application Development (2024)"}
    ]
    create_pdf(os.path.join(output_dir, "03_Resume_A.pdf"), "Resume — Rohan Malhotra", resume_a_blocks)

    # 3. Resume B: Maya Lin
    resume_b_blocks = [
        {"type": "h2", "text": "Maya Lin — Full-Stack AI Engineer"},
        {"type": "p", "text": "<b>Email:</b> maya.lin@devstudio.io | <b>Phone:</b> +1 (555) 048-9120"},
        {"type": "h2", "text": "Summary"},
        {"type": "p", "text": "Pragmatic AI Engineer with 4 years of experience building Python microservices and React dashboards. Expert in leveraging AI coding tools (Claude Code, Cursor) to rapidly build, debug, and maintain production freight applications. Strong focus on reliability and UI operator workflow."},
        {"type": "h2", "text": "Work Experience"},
        {"type": "p", "text": "<b>AI Systems Engineer — FreightPulse Inc.</b> (Mar 2024 – Present, 1.4 years)"},
        {"type": "p", "text": "• Built interactive operator dashboards in React.js connected to FastAPI backends for real-time shipment tracking and exception resolution."},
        {"type": "p", "text": "• Directed AI coding assistants (Claude Code, Cursor) to accelerate backend feature generation, unit testing, and carrier API integration by 3x."},
        {"type": "p", "text": "• Built OCR invoice processing pipeline using AWS Textract & Python, resolving carrier line-item discrepancies automatically."},
        {"type": "p", "text": "• Served on-call rotation for production freight systems; maintained 99.9% uptime by resolving agent loop failures within minutes."},
        {"type": "p", "text": "<b>Software Engineer — LogiTech Logistics</b> (Jun 2021 – Feb 2024, 2.7 years)"},
        {"type": "p", "text": "• Developed REST APIs with Python/FastAPI and MongoDB for carrier booking and rate calculation."},
        {"type": "p", "text": "• Built vector search indexing pipeline (FAISS) to parse unstructured carrier rate cards."},
        {"type": "h2", "text": "Skills"},
        {"type": "p", "text": "Python, FastAPI, React.js, Next.js, Claude Code, Cursor, AI Prompting, MongoDB, RAG, AWS Textract (OCR), REST APIs, Docker, Git."},
        {"type": "h2", "text": "Education"},
        {"type": "p", "text": "B.S. Computer Engineering, UC Berkeley, 2021"}
    ]
    create_pdf(os.path.join(output_dir, "04_Resume_B.pdf"), "Resume — Maya Lin", resume_b_blocks)

    # 4. Transcript A: Rohan Malhotra
    transcript_a_blocks = [
        {"type": "h2", "text": "Candidate Interview Transcript: Rohan Malhotra"},
        {"type": "p", "text": "<b>Interviewer:</b> Sarah Jenkins (VP of Engineering) | <b>Candidate:</b> Rohan Malhotra"},
        {"type": "spacer", "height": 10},
        
        {"type": "speaker", "text": "Sarah (Interviewer):"},
        {"type": "p", "text": "Welcome Rohan. Thanks for joining. Let's start with your experience at Voltrix building multi-agent freight ops platforms."},
        
        {"type": "speaker", "text": "Rohan Malhotra:"},
        {"type": "p", "text": "Thanks Sarah! Yeah, at Voltrix I architected our exception-handling engine end-to-end. We used a planner-executor-reviewer pattern with LangGraph and CrewAI. It processes over 5,000 exceptions monthly, cutting manual review time by 40%. I also optimized prompts across GPT-4 and SLMs, cutting costs by 30%."},
        
        {"type": "speaker", "text": "Sarah (Interviewer):"},
        {"type": "p", "text": "That's impressive. How do you approach using AI coding assistants like Claude Code in your daily workflow? Our team heavily relies on directing Claude Code to build features fast."},
        
        {"type": "speaker", "text": "Rohan Malhotra:"},
        {"type": "p", "text": "Honestly, I don't trust AI coding tools like Claude Code or Copilot. I write all my Python code manually line by line and forbid auto-generated code in my work because it introduces tech debt and sloppy code. I believe real senior engineers should write every line of code themselves rather than relying on tools like Claude Code."},
        
        {"type": "speaker", "text": "Sarah (Interviewer):"},
        {"type": "p", "text": "I see. Moving on, our job requires building React frontend screens for operators. Can you walk me through your React experience?"},
        
        {"type": "speaker", "text": "Rohan Malhotra:"},
        {"type": "p", "text": "Well, my resume lists React basic skills, but to be completely honest, I haven't written front-end React code in over two years. At Nimbus and Voltrix, the front-end engineers handled all the React components. I mostly deal with Python APIs."},
        
        {"type": "speaker", "text": "Sarah (Interviewer):"},
        {"type": "p", "text": "Okay. Tell me about a time a production agent system failed while you were on call, and how you handled it."},
        
        {"type": "speaker", "text": "Rohan Malhotra:"},
        {"type": "p", "text": "Ah, last quarter our exception agent got stuck in an infinite retry loop and crashed. Honestly, that wasn't really my fault — the infrastructure team misconfigured the Kubernetes pod limits and didn't notify me. Once devops fixed their container limits, the system worked again."},
        
        {"type": "speaker", "text": "Sarah (Interviewer):"},
        {"type": "p", "text": "On your resume, it says you led a 4-person team migrating a legacy monolith to microservices at Nimbus right after graduating in 2022. Could you clarify your leadership role there?"},
        
        {"type": "speaker", "text": "Rohan Malhotra:"},
        {"type": "p", "text": "Well, 'led' might be slightly strong for the whole project. I was a junior dev just out of college in Aug 2022, but I helped coordinate the database migration sub-task among 3 other devs. The principal architect officially led the overall migration."}
    ]
    create_pdf(os.path.join(output_dir, "05_Transcript_A.pdf"), "Transcript — Rohan Malhotra", transcript_a_blocks)

    # 5. Transcript B: Maya Lin
    transcript_b_blocks = [
        {"type": "h2", "text": "Candidate Interview Transcript: Maya Lin"},
        {"type": "p", "text": "<b>Interviewer:</b> Sarah Jenkins (VP of Engineering) | <b>Candidate:</b> Maya Lin"},
        {"type": "spacer", "height": 10},
        
        {"type": "speaker", "text": "Sarah (Interviewer):"},
        {"type": "p", "text": "Hi Maya! Thanks for taking the time. To start, how do you work with AI coding tools like Claude Code?"},
        
        {"type": "speaker", "text": "Maya Lin:"},
        {"type": "p", "text": "Hi Sarah! Directing AI tools like Claude Code and Cursor is central to my daily development. I write tight spec prompts, review the generated Python and React diffs, write unit tests to verify the logic, and iterate. It allows me to ship backend endpoints and React screens 3 times faster than manual coding."},
        
        {"type": "speaker", "text": "Sarah (Interviewer):"},
        {"type": "p", "text": "Great! How do you handle frontend React requirements alongside Python backends?"},
        
        {"type": "speaker", "text": "Maya Lin:"},
        {"type": "p", "text": "At FreightPulse, I owned full-stack operator screens. I build React interfaces with state management to let dispatchers see live shipment statuses and override agent decisions. On the backend, I write FastAPI endpoints and MongoDB queries."},
        
        {"type": "speaker", "text": "Sarah (Interviewer):"},
        {"type": "p", "text": "How do you handle production outages when an AI agent misbehaves?"},
        
        {"type": "speaker", "text": "Maya Lin:"},
        {"type": "p", "text": "I take direct personal ownership. Last month, an OCR parser failed on a corrupted carrier bill of lading, causing our booking agent to halt. I jumped on call, added guardrails and fallback parsing in Python within 20 minutes, deployed the patch, and added automated regression tests so it wouldn't happen again."},
        
        {"type": "speaker", "text": "Sarah (Interviewer):"},
        {"type": "p", "text": "What about complex multi-agent frameworks like LangGraph or CrewAI?"},
        
        {"type": "speaker", "text": "Maya Lin:"},
        {"type": "p", "text": "To be transparent, I haven't built heavy custom multi-agent orchestrators using LangGraph from scratch yet. My experience has been with focused agent loops, RAG pipelines, and API integrations. But I am eager to learn LangGraph and scale multi-agent patterns here."}
    ]
    create_pdf(os.path.join(output_dir, "06_Transcript_B.pdf"), "Transcript — Maya Lin", transcript_b_blocks)

if __name__ == "__main__":
    generate_all_pdfs()
