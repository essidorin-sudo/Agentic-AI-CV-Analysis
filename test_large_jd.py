#!/usr/bin/env python3
"""Test with a JD over 6000 characters to verify controlled redaction"""

import sys
import os
sys.path.append('/Users/eugenes/Desktop/Agentic-AI-CV-Analysis/production-system/backend')

# Create a JD that's definitely over 6000 characters
large_jd = """Senior Software Engineer Position
San Francisco, CA | Full-Time | $120,000 - $160,000

ABOUT THE ROLE:
We are seeking a highly skilled Senior Software Engineer to join our dynamic engineering team. In this role, you will be responsible for designing, developing, and maintaining scalable web applications that serve millions of users worldwide. You will work closely with product managers, designers, and other engineers to deliver high-quality software solutions that make a real impact on our users' lives.

Our engineering culture emphasizes collaboration, innovation, and continuous learning. We believe in giving engineers the autonomy to make technical decisions while providing the support and resources needed to succeed. This is an excellent opportunity for a senior engineer who wants to take on technical leadership responsibilities and help shape the future of our platform.

REQUIREMENTS:
• 5+ years of professional Python development experience with frameworks like Django, Flask, or FastAPI
• Strong experience with React and modern JavaScript frameworks including TypeScript, Next.js, and state management libraries
• Proficiency with AWS cloud platform and containerization technologies (Docker, Kubernetes, ECS)
• Experience with Docker containerization and deployment strategies in production environments
• Database design experience, preferably PostgreSQL and NoSQL databases like MongoDB or DynamoDB
• Leadership experience mentoring junior developers and conducting thorough code reviews
• Bachelor's degree in Computer Science, Software Engineering, or related technical field
• Experience with version control systems (Git) and CI/CD pipelines using tools like Jenkins, GitLab CI, or GitHub Actions
• Strong understanding of RESTful API design principles and microservices architecture patterns
• Solid foundation in computer science fundamentals including algorithms, data structures, and system design
• Experience with testing methodologies including unit testing, integration testing, and end-to-end testing
• Understanding of security best practices and common vulnerabilities (OWASP guidelines)

RESPONSIBILITIES:
• Lead development of scalable web applications and APIs using modern technologies and best practices
• Mentor and guide junior developers in technical skills, code quality, and professional development
• Design and implement system architecture and technical solutions for complex business problems
• Deploy and maintain cloud infrastructure on AWS using infrastructure as code tools like Terraform or CloudFormation
• Collaborate with product and design teams on feature development and technical requirements gathering
• Participate in code reviews and maintain high coding standards across the engineering team
• Optimize application performance and ensure scalability for growing user base and data volumes
• Troubleshoot production issues and implement comprehensive monitoring and alerting solutions
• Stay up-to-date with emerging technologies and recommend improvements to existing systems
• Contribute to engineering culture by participating in tech talks, documentation, and knowledge sharing
• Work with DevOps team to implement robust deployment pipelines and monitoring solutions
• Participate in on-call rotations to ensure system reliability and quick incident response

NICE TO HAVE:
• Experience with microservices architecture and distributed systems design patterns
• Knowledge of machine learning and AI technologies, particularly in production environments
• Experience with agile development methodologies (Scrum, Kanban) and project management tools
• Open source contributions and active participation in the developer community
• Experience with mobile development, particularly React Native or native iOS/Android development
• Familiarity with DevOps practices and tools including monitoring, logging, and observability
• Experience with data visualization libraries and frameworks like D3.js, Chart.js, or similar
• Understanding of performance optimization techniques for both frontend and backend systems
• Experience with real-time systems and technologies like WebSockets, Server-Sent Events, or similar
• Knowledge of blockchain technologies and cryptocurrency systems
• Experience with content delivery networks (CDNs) and edge computing platforms

TECHNICAL SKILLS:
• Programming Languages: Python, JavaScript, TypeScript, SQL, HTML, CSS, Go, Java
• Frameworks: Flask, Django, FastAPI, React, Vue.js, Angular, Node.js, Express, Spring Boot
• Cloud Services: AWS (EC2, S3, RDS, Lambda, CloudWatch, ELB), Azure, Google Cloud Platform
• Databases: PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch, DynamoDB, Cassandra
• DevOps Tools: Docker, Kubernetes, Jenkins, GitLab CI, GitHub Actions, Terraform, Ansible
• Testing: Jest, PyTest, Selenium, Cypress, Mocha, JUnit, TestNG
• Version Control: Git, GitHub, GitLab, Bitbucket
• Monitoring: New Relic, DataDog, Prometheus, Grafana, Splunk, ELK Stack
• Message Queues: RabbitMQ, Apache Kafka, Amazon SQS, Redis Pub/Sub
• API Tools: Postman, Swagger, GraphQL, REST, gRPC

WHAT WE OFFER:
• Competitive salary range of $120,000 - $160,000 based on experience and qualifications
• Comprehensive health, dental, and vision insurance with company contribution of 90% of premiums
• 401(k) retirement plan with company matching up to 6% of salary
• Flexible paid time off policy and personal development days for conferences and learning
• $2,000 annual learning and development budget for courses, conferences, and certifications
• Remote-friendly work environment with flexible hours and core collaboration time
• State-of-the-art equipment including MacBook Pro, external monitors, and ergonomic office setup
• Home office setup allowance of $1,500 for remote employees
• Team building events, company retreats, and regular social activities
• Stock option program for long-term growth and company success sharing
• Comprehensive parental leave policy with 12 weeks paid leave
• Mental health support through therapy coverage and wellness programs
• Commuter benefits and gym membership reimbursement
• Free meals, snacks, and beverages in the office
• Professional development opportunities including conference attendance and speaking opportunities

COMPANY CULTURE:
We believe in fostering an inclusive and collaborative work environment where every team member can thrive and do their best work. Our company values innovation, continuous learning, and maintaining a healthy work-life balance. We encourage experimentation, celebrate failures as learning opportunities, and support each other's professional growth through mentorship and knowledge sharing.

Our team consists of passionate engineers, designers, and product managers who are committed to building products that make a positive impact on people's lives. We value diversity of thought and background, and we're committed to building a team that reflects the diversity of our user base.

We practice transparent communication, regular feedback, and collaborative decision-making. Our engineering team follows agile methodologies with regular sprint planning, retrospectives, and continuous improvement processes.

APPLICATION PROCESS:
To apply, please submit your resume along with a detailed cover letter explaining why you're interested in this position and how your experience aligns with our requirements. We also encourage you to include links to your GitHub profile, portfolio, or any relevant side projects that demonstrate your technical skills.

We review applications on a rolling basis and aim to respond to all qualified candidates within one week. Our interview process typically consists of an initial phone screen, a technical coding challenge, an on-site interview with multiple team members, and a final culture fit conversation with leadership.

We are an equal opportunity employer committed to diversity and inclusion. We welcome applications from all qualified candidates regardless of race, gender, age, religion, sexual orientation, disability status, veteran status, or any other protected characteristic."""

print(f"📏 Large JD length: {len(large_jd)} characters")

if len(large_jd) > 6000:
    print("✅ JD is over 6000 chars - will trigger redaction")
    
    try:
        from app import app
        
        test_jd_data = {
            'raw_text': large_jd,
            'company_name': 'Test Company',
            'job_title': 'Senior Software Engineer'
        }
        
        with app.app_context():
            def redact_jd_content(parsed_data):
                """Minimal redaction of JD content only if over 10,000 characters"""
                if not parsed_data or not parsed_data.get('raw_text'):
                    return parsed_data
                
                raw_text = parsed_data['raw_text']
                
                if len(raw_text) <= 6000:
                    return parsed_data
                
                print(f"🔍 JD raw_text length: {len(raw_text)} chars - applying minimal redaction for Gap Analyst (>6k limit)")
                
                redacted_text = raw_text
                
                if parsed_data.get('company_name') and parsed_data['company_name'] != 'Unknown':
                    company_name = parsed_data['company_name']
                    redacted_text = redacted_text.replace(company_name, "[COMPANY NAME REDACTED]")
                
                import re
                company_patterns = [
                    r'About\s+[A-Z][a-z]+\s+Company[:\n].*?(?=\n\n[A-Z]|REQUIREMENTS|QUALIFICATIONS|RESPONSIBILITIES|$)',
                    r'Company\s+Overview[:\n].*?(?=\n\n[A-Z]|REQUIREMENTS|QUALIFICATIONS|RESPONSIBILITIES|$)',
                    r'Our\s+Mission[:\n].*?(?=\n\n[A-Z]|REQUIREMENTS|QUALIFICATIONS|RESPONSIBILITIES|$)',
                    r'Benefits\s+Package[:\n].*?(?=\n\n[A-Z]|$)',
                ]
                
                for pattern in company_patterns:
                    test_result = re.sub(pattern, '[COMPANY INFO REDACTED]', redacted_text, flags=re.DOTALL | re.IGNORECASE)
                    if len(test_result) >= len(redacted_text) * 0.7:
                        redacted_text = test_result
                
                redacted_data = parsed_data.copy()
                redacted_data['raw_text'] = redacted_text
                
                print(f"🔍 Redacted JD from {len(raw_text)} to {len(redacted_text)} chars")
                return redacted_data
            
            result = redact_jd_content(test_jd_data)
            
            original_length = len(test_jd_data['raw_text'])
            redacted_length = len(result['raw_text'])
            reduction_percent = ((original_length - redacted_length) / original_length) * 100
            
            print(f"📊 LARGE JD REDACTION RESULTS:")
            print(f"   • Original: {original_length} chars")
            print(f"   • Redacted: {redacted_length} chars") 
            print(f"   • Reduced by: {reduction_percent:.1f}%")
            print(f"   • Retained: {100 - reduction_percent:.1f}%")
            
            if redacted_length >= original_length * 0.7:
                print("✅ SUCCESS: Large JD redaction preserves >70% of content")
                
                # Check that important sections are preserved
                redacted_content = result['raw_text']
                has_requirements = 'REQUIREMENTS' in redacted_content
                has_responsibilities = 'RESPONSIBILITIES' in redacted_content
                
                print(f"📋 Content check:")
                print(f"   • REQUIREMENTS section preserved: {has_requirements}")
                print(f"   • RESPONSIBILITIES section preserved: {has_responsibilities}")
                
                if has_requirements and has_responsibilities:
                    print("✅ EXCELLENT: Key job sections preserved!")
                    print("🎯 This should provide Gap Analyst with enough content for mixed highlighting")
                else:
                    print("⚠️  Some key sections may have been removed")
                    
            else:
                print("❌ ISSUE: Still removing too much content from large JDs")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback  
        traceback.print_exc()
        
else:
    print("❌ JD not large enough to trigger redaction - make it bigger")