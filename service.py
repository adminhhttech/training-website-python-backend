import tempfile
import random
from dataclasses import dataclass
from typing import Dict, List, Optional
from uuid import uuid4

from engine import classify_answer, should_repeat, update_score
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

DOMAINS: List[str] = [
    "backend",
    "frontend",
    "data analytics",
    "machine learning",
    "devops",
    "cybersecurity",
    "data engineering",
    "algorithms",
]

DOMAIN_TOPICS: Dict[str, List[str]] = {
    "backend": [
        "REST APIs",
        "SQL databases",
        "authentication",
        "caching",
        "microservices basics",
        "Docker",
        "cloud deployment",
    ],
    "frontend": [
        "semantic HTML",
        "CSS layouts",
        "JavaScript ES6+",
        "responsive design",
        "React fundamentals",
        "state management",
        "performance optimization",
    ],
    "data analytics": [
        "SQL querying",
        "data cleaning",
        "data visualization",
        "statistics fundamentals",
        "dashboard building",
        "A/B testing basics",
        "business storytelling",
    ],
    "machine learning": [
        "supervised learning",
        "model evaluation",
        "feature engineering",
        "unsupervised learning",
        "deep learning basics",
        "model deployment",
        "MLOps fundamentals",
    ],
    "devops": [
        "CI/CD pipelines",
        "Docker",
        "monitoring",
        "Kubernetes basics",
        "infrastructure as code",
        "cloud operations",
        "incident response",
    ],
    "cybersecurity": [
        "network security",
        "threat detection",
        "incident response",
        "OWASP Top 10",
        "identity and access management",
        "vulnerability assessment",
        "security monitoring",
    ],
    "data engineering": [
        "ETL pipelines",
        "data warehousing",
        "stream processing",
        "data modeling",
        "orchestration tools",
        "distributed processing",
        "data quality checks",
    ],
    "algorithms": [
        "data structures",
        "time complexity",
        "dynamic programming",
        "graph algorithms",
        "greedy techniques",
        "recursion and backtracking",
        "problem-solving patterns",
    ],
}

DOMAIN_PROJECTS: Dict[str, List[str]] = {
    "backend": [
        "Build a REST API with authentication",
        "Create a CRUD app with database integration",
        "Deploy a backend service on cloud",
    ],
    "frontend": [
        "Build a responsive landing page",
        "Create a React dashboard with charts",
        "Develop a small PWA with offline support",
    ],
    "data analytics": [
        "Analyze a public dataset and create a report",
        "Build a dashboard in Tableau/Power BI",
        "Write SQL queries for business insights",
    ],
    "machine learning": [
        "Train a classifier on tabular data",
        "Build an end-to-end ML pipeline",
        "Deploy a model behind an API",
    ],
    "devops": [
        "Set up CI/CD for a sample app",
        "Containerize an app with Docker",
        "Add monitoring and alerting",
    ],
    "cybersecurity": [
        "Perform a basic vulnerability assessment",
        "Harden a web app against OWASP Top 10",
        "Create an incident response checklist",
    ],
    "data engineering": [
        "Build an ETL pipeline",
        "Create a streaming ingestion prototype",
        "Design a warehouse schema for analytics",
    ],
    "algorithms": [
        "Solve 50 mixed DSA problems",
        "Implement classic data structures from scratch",
        "Build a dynamic programming problem set tracker",
    ],
}

TOPIC_EXPLANATIONS: Dict[str, str] = {
    "REST APIs": "REST APIs are HTTP-based interfaces for exchanging data between services using resources and verbs.",
    "SQL databases": "SQL databases store relational data with schemas, constraints, and ACID guarantees.",
    "authentication": "Authentication verifies identity before allowing access to protected features.",
    "caching": "Caching stores frequently used data temporarily to reduce latency and backend load.",
    "microservices basics": "Microservices split an application into smaller independent services with clear boundaries.",
    "Docker": "Docker packages application code and dependencies into portable, reproducible containers.",
    "cloud deployment": "Cloud deployment runs applications on scalable managed infrastructure and services.",
    "semantic HTML": "Semantic HTML uses meaningful elements to improve accessibility, structure, and SEO.",
    "CSS layouts": "CSS layouts with Flexbox and Grid create responsive and maintainable page structures.",
    "JavaScript ES6+": "ES6+ introduces modern JavaScript syntax and features for cleaner code.",
    "responsive design": "Responsive design adapts UI across screen sizes for consistent user experience.",
    "React fundamentals": "React fundamentals cover components, props, state, hooks, and rendering flow.",
    "state management": "State management controls how UI data is stored, updated, and shared.",
    "performance optimization": "Performance optimization improves load time, rendering speed, and app responsiveness.",
    "SQL querying": "SQL querying retrieves and transforms data using filters, joins, grouping, and aggregates.",
    "data cleaning": "Data cleaning fixes missing, duplicate, and inconsistent records before analysis.",
    "data visualization": "Data visualization presents information clearly with charts that reveal patterns.",
    "statistics fundamentals": "Statistics fundamentals explain distributions, variability, and inference from samples.",
    "dashboard building": "Dashboard building combines KPIs and visuals into actionable decision views.",
    "A/B testing basics": "A/B testing compares variants to measure impact using statistical confidence.",
    "business storytelling": "Business storytelling turns analysis into clear recommendations for stakeholders.",
    "supervised learning": "Supervised learning maps labeled inputs to outputs for prediction tasks.",
    "model evaluation": "Model evaluation uses metrics and validation to check model quality and generalization.",
    "feature engineering": "Feature engineering creates useful inputs that improve model performance.",
    "unsupervised learning": "Unsupervised learning finds hidden patterns in unlabeled data.",
    "deep learning basics": "Deep learning uses multi-layer neural networks to learn complex representations.",
    "model deployment": "Model deployment serves trained models in production systems.",
    "MLOps fundamentals": "MLOps applies DevOps practices to machine learning lifecycle management.",
    "CI/CD pipelines": "CI/CD pipelines automate build, test, and deployment workflows.",
    "monitoring": "Monitoring tracks system health, errors, and performance over time.",
    "Kubernetes basics": "Kubernetes orchestrates containerized applications across clusters.",
    "infrastructure as code": "Infrastructure as code provisions and manages infra using versioned code.",
    "cloud operations": "Cloud operations covers reliability, security, and cost-efficient cloud management.",
    "incident response": "Incident response is the structured process to detect and recover from outages or attacks.",
    "network security": "Network security protects systems with segmentation, filtering, and secure communication.",
    "threat detection": "Threat detection identifies malicious behavior through logs, telemetry, and alerts.",
    "OWASP Top 10": "OWASP Top 10 highlights common web application security risks.",
    "identity and access management": "IAM manages authentication, authorization, and least-privilege access.",
    "vulnerability assessment": "Vulnerability assessment finds and prioritizes security weaknesses.",
    "security monitoring": "Security monitoring continuously observes systems for suspicious activity.",
    "ETL pipelines": "ETL pipelines extract, transform, and load data for analytics systems.",
    "data warehousing": "Data warehousing stores integrated historical data for reporting and BI.",
    "stream processing": "Stream processing handles data in real time as events arrive.",
    "data modeling": "Data modeling defines structures and relationships for efficient querying.",
    "orchestration tools": "Orchestration tools schedule and manage multi-step data workflows.",
    "distributed processing": "Distributed processing scales workloads across multiple machines.",
    "data quality checks": "Data quality checks validate completeness, accuracy, and consistency.",
    "data structures": "Data structures organize data for efficient storage and retrieval.",
    "time complexity": "Time complexity estimates algorithm growth as input size increases.",
    "dynamic programming": "Dynamic programming solves overlapping subproblems with memoization or tabulation.",
    "graph algorithms": "Graph algorithms process relationships like paths, connectivity, and traversal.",
    "greedy techniques": "Greedy techniques build solutions by choosing locally optimal steps.",
    "recursion and backtracking": "Recursion and backtracking explore possibilities with controlled rollback.",
    "problem-solving patterns": "Problem-solving patterns are reusable strategies for algorithm design.",
}


@dataclass
class Session:
    user_name: Optional[str] = None
    user_location: Optional[str] = None
    user_education: Optional[str] = None
    selected_domain: Optional[str] = None
    question_count: int = 0
    score: int = 0
    docs_shown: bool = False
    pending_domain_switch: Optional[str] = None


class CounsellorService:
    def __init__(self) -> None:
        self.sessions: Dict[str, Session] = {}

    def start(self) -> str:
        session_id = str(uuid4())
        self.sessions[session_id] = Session()
        return session_id

    def get_domains(self) -> List[str]:
        return DOMAINS

    def submit_personal_info(
        self,
        session_id: str,
        name: Optional[str] = None,
        location: Optional[str] = None,
        education: Optional[str] = None,
    ) -> Dict:
        state = self.sessions.get(session_id)
        if not state:
            return {"message": "Session not found"}

        if name:
            state.user_name = name.strip()
        if location:
            state.user_location = location.strip()
        if education:
            state.user_education = education.strip()

        return {
            "message": "Thanks for the information!",
            "question": "Which tech domain interests you?",
        }

    def answer(self, session_id: str, answer: str) -> Dict:
        pending_result = {"level": "", "score": 0, "total": 0}
        state = self.sessions.get(session_id)
        if not state:
            return {"message": "Session not found", "completed": True, "result": pending_result}

        user_text = answer.strip().lower()

        if not state.selected_domain:
            domain = self._match_domain(user_text)
            if not domain:
                return {
                    "message": "Select one domain first.",
                    "question": "Choose: Backend, Frontend, Data Analytics, Machine Learning, DevOps, Cybersecurity, Data Engineering, Algorithms.",
                    "completed": False,
                    "result": pending_result,
                }
            state.selected_domain = domain
            state.question_count = 0
            state.score = 0
            user_name = state.user_name or "there"
            return {
                "message": f"Excellent choice, {user_name}! Let's assess your {domain} skills.",
                "question": self._questions(domain)[0],
                "completed": False,
                "result": pending_result,
            }

        questions = self._questions(state.selected_domain)
        if should_repeat(user_text):
            return {
                "message": "Please answer with yes or no.",
                "question": questions[state.question_count],
                "completed": False,
                "result": pending_result,
            }

        answer_type = classify_answer(user_text)
        current_topic = DOMAIN_TOPICS[state.selected_domain][state.question_count]
        info_message = ""
        if answer_type == "NO":
            info_message = self._topic_info(current_topic, state.selected_domain)

        update_score(state, user_text, 1)
        state.question_count += 1

        if state.question_count >= len(questions):
            total = len(questions)
            pct = (state.score / total) * 100
            level = "Beginner" if pct < 40 else "Intermediate" if pct < 75 else "Advanced"
            result = {"level": level, "score": state.score, "total": total}
            recommendations = self._recommendations(
                domain=state.selected_domain,
                score=state.score,
                total=total,
                level=level,
            )
            return {
                "message": f"{info_message}\n\nAssessment completed.".strip() if info_message else "Assessment completed.",
                "completed": True,
                "domain": state.selected_domain,
                "score": state.score,
                "total": total,
                "level": level,
                "result": result,
                "recommendations": recommendations,
            }

        response = {"question": questions[state.question_count], "completed": False, "result": pending_result}
        if info_message:
            response["message"] = info_message
        return response

    def detailed_roadmap(self, session_id: Optional[str], domain: Optional[str]) -> Dict:
        selected = (domain or "").strip().lower()
        if not selected and session_id and session_id in self.sessions:
            selected = self.sessions[session_id].selected_domain or ""
        if selected not in DOMAINS:
            selected = "frontend"
        if selected == "data analytics":
            return {
                "domain": selected,
                "title": "Data Analytics Roadmap",
                "description": "Complete guide to becoming a proficient data analyst",
                "prerequisites": "Basic mathematics and statistics knowledge",
                "duration": "5-7 months with consistent practice",
                "steps": [
                    {
                        "step": 1,
                        "title": "Data Foundations",
                        "duration": "3-4 weeks",
                        "topics": [
                            "Statistics fundamentals",
                            "Data types and structures",
                            "Excel/Google Sheets mastery",
                            "Basic data visualization principles",
                            "Data collection methods",
                        ],
                        "projects": [
                            "Sales data analysis in Excel",
                            "Statistical analysis report",
                            "Basic charts and graphs",
                        ],
                        "resources": [
                            {"title": "Khan Academy Statistics", "url": "https://www.khanacademy.org/math/statistics-probability"},
                            {"title": "Excel Tutorial", "url": "https://support.microsoft.com/en-us/office/excel-help-center"},
                            {"title": "Data Visualization Guide", "url": "https://www.tableau.com/learn/articles/data-visualization"},
                        ],
                    },
                    {
                        "step": 2,
                        "title": "SQL Mastery",
                        "duration": "4-5 weeks",
                        "topics": [
                            "SQL fundamentals and syntax",
                            "Complex joins and subqueries",
                            "Window functions and CTEs",
                            "Data aggregation and grouping",
                            "Query optimization techniques",
                        ],
                        "projects": [
                            "Database analysis project",
                            "Complex query challenges",
                            "Data extraction pipeline",
                        ],
                        "resources": [
                            {"title": "W3Schools SQL", "url": "https://www.w3schools.com/sql/"},
                            {"title": "SQLBolt Interactive Tutorial", "url": "https://sqlbolt.com/"},
                            {"title": "PostgreSQL Tutorial", "url": "https://www.postgresqltutorial.com/"},
                        ],
                    },
                    {
                        "step": 3,
                        "title": "Python for Data Analysis",
                        "duration": "6-8 weeks",
                        "topics": [
                            "Python basics and data structures",
                            "Pandas for data manipulation",
                            "NumPy for numerical computing",
                            "Data cleaning and preprocessing",
                            "Jupyter notebook workflows",
                        ],
                        "projects": [
                            "Data cleaning project",
                            "Exploratory data analysis",
                            "Automated reporting script",
                        ],
                        "resources": [
                            {"title": "Pandas Documentation", "url": "https://pandas.pydata.org/docs/"},
                            {"title": "Python for Data Analysis Book", "url": "https://wesmckinney.com/book/"},
                            {"title": "Kaggle Learn Python", "url": "https://www.kaggle.com/learn/python"},
                        ],
                    },
                    {
                        "step": 4,
                        "title": "Data Visualization",
                        "duration": "4-5 weeks",
                        "topics": [
                            "Matplotlib and Seaborn",
                            "Interactive visualizations",
                            "Dashboard design principles",
                            "Storytelling with data",
                            "Color theory and accessibility",
                        ],
                        "projects": [
                            "Interactive dashboard",
                            "Data story presentation",
                            "Visualization library",
                        ],
                        "resources": [
                            {"title": "Matplotlib Documentation", "url": "https://matplotlib.org/stable/contents.html"},
                            {"title": "Seaborn Tutorial", "url": "https://seaborn.pydata.org/tutorial.html"},
                            {"title": "Plotly Documentation", "url": "https://plotly.com/python/"},
                        ],
                    },
                    {
                        "step": 5,
                        "title": "Business Intelligence Tools",
                        "duration": "5-6 weeks",
                        "topics": [
                            "Tableau fundamentals",
                            "Power BI development",
                            "Dashboard best practices",
                            "KPI identification and tracking",
                            "Report automation",
                        ],
                        "projects": [
                            "Executive dashboard",
                            "Sales performance tracker",
                            "Automated reporting system",
                        ],
                        "resources": [
                            {"title": "Tableau Learning", "url": "https://www.tableau.com/learn"},
                            {"title": "Power BI Documentation", "url": "https://docs.microsoft.com/en-us/power-bi/"},
                            {"title": "BI Best Practices", "url": "https://www.sisense.com/blog/business-intelligence-best-practices/"},
                        ],
                    },
                    {
                        "step": 6,
                        "title": "Advanced Analytics",
                        "duration": "6-7 weeks",
                        "topics": [
                            "Statistical hypothesis testing",
                            "A/B testing and experimentation",
                            "Predictive analytics basics",
                            "Time series analysis",
                            "Machine learning for analysts",
                        ],
                        "projects": [
                            "A/B test analysis",
                            "Forecasting model",
                            "Customer segmentation",
                        ],
                        "resources": [
                            {"title": "Statistical Methods", "url": "https://www.statmethods.net/"},
                            {"title": "A/B Testing Guide", "url": "https://blog.hubspot.com/marketing/how-to-do-a-b-testing"},
                            {"title": "Scikit-learn", "url": "https://scikit-learn.org/stable/user_guide.html"},
                        ],
                    },
                ],
                "career_paths": [
                    "Data Analyst",
                    "Business Analyst",
                    "Marketing Analyst",
                    "Financial Analyst",
                    "Data Scientist",
                ],
                "tips": [
                    "Focus on understanding business context",
                    "Practice storytelling with data",
                    "Learn to ask the right questions",
                    "Master data cleaning and validation",
                    "Stay curious and keep learning new tools",
                ],
            }

        return self._default_roadmap(selected)

    def generate_roadmap_pdf(self, session_id: Optional[str], domain: Optional[str]) -> str:
        roadmap = self.detailed_roadmap(session_id=session_id, domain=domain)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        doc = SimpleDocTemplate(tmp.name, pagesize=A4)
        styles = getSampleStyleSheet()
        story = [
            Paragraph(roadmap["title"], styles["Title"]),
            Spacer(1, 8),
            Paragraph(roadmap["description"], styles["Normal"]),
            Spacer(1, 8),
            Paragraph(f"Duration: {roadmap['duration']}", styles["Normal"]),
            Spacer(1, 12),
        ]
        for step in roadmap["steps"]:
            story.append(Paragraph(f"Step {step['step']}: {step['title']}", styles["Heading2"]))
            story.append(Paragraph(f"Duration: {step['duration']}", styles["Normal"]))
            story.append(Spacer(1, 4))
            story.append(Paragraph("Topics to Learn:", styles["Heading3"]))
            for topic in step["topics"]:
                story.append(Paragraph(f"- {topic}", styles["Normal"]))
            story.append(Spacer(1, 4))
            story.append(Paragraph("Practice Projects:", styles["Heading3"]))
            for project in step.get("projects", []):
                story.append(Paragraph(f"- {project}", styles["Normal"]))
            story.append(Spacer(1, 4))
            story.append(Paragraph("Learning Resources:", styles["Heading3"]))
            for resource in step.get("resources", []):
                story.append(Paragraph(f"- {resource['title']}: {resource['url']}", styles["Normal"]))
            story.append(Spacer(1, 8))

        story.append(Spacer(1, 10))
        story.append(Paragraph("Career Opportunities", styles["Heading2"]))
        for career in roadmap.get("career_paths", []):
            story.append(Paragraph(f"- {career}", styles["Normal"]))

        story.append(Spacer(1, 10))
        story.append(Paragraph("Success Tips", styles["Heading2"]))
        for tip in roadmap.get("tips", []):
            story.append(Paragraph(f"- {tip}", styles["Normal"]))

        doc.build(story)
        return tmp.name

    def submit_feedback(self, session_id: Optional[str], feedback: str) -> Dict:
        if not session_id or session_id not in self.sessions:
            return {"message": "Thank you for your feedback!"}
        state = self.sessions[session_id]
        domain = state.selected_domain or "frontend"
        user_name = state.user_name or "there"
        return {
            "message": f"Thank you for your valuable feedback, {user_name}!",
            "docs": self._docs(domain),
        }

    def chat(self, session_id: str, message: str) -> Dict:
        state = self.sessions.get(session_id)
        if not state:
            return {"message": "Session not found"}

        text = message.lower().strip()
        mentioned_domain = self._match_domain(text)
        if mentioned_domain and mentioned_domain != state.selected_domain:
            state.pending_domain_switch = mentioned_domain
            return {
                "message": f"I see you're interested in {mentioned_domain}. Say 'yes' to switch roadmap.",
                "switch_domain": mentioned_domain,
            }

        if state.pending_domain_switch and text in {"yes", "y", "ok", "okay", "sure"}:
            state.selected_domain = state.pending_domain_switch
            state.pending_domain_switch = None
            return {
                "message": f"Great! Switched to {state.selected_domain}.",
                "generate_roadmap": state.selected_domain,
            }

        domain = state.selected_domain or "frontend"
        if any(word in text for word in ["thank", "thanks", "appreciate"]):
            return {"message": "You're welcome. Happy to help."}

        if any(word in text for word in ["improve", "better", "learn", "study", "focus", "next"]):
            return {
                "message": f"Focus on core {domain} fundamentals, then build 2 projects.",
                "docs": self._docs(domain),
            }

        if any(word in text for word in ["how", "what", "why", "help", "guide", "tutorial"]):
            if not state.docs_shown:
                state.docs_shown = True
                return {
                    "message": "Use these official resources:",
                    "docs": self._docs(domain),
                }
            return {"message": "Please share a specific question and I will help directly."}

        return {
            "message": "I can help with roadmap, improvement plan, or domain switch. Ask anything specific."
        }

    def _questions(self, domain: str) -> List[str]:
        return [f"Do you have experience with {topic}?" for topic in DOMAIN_TOPICS[domain]]

    def _match_domain(self, text: str) -> Optional[str]:
        alias_map = {
            "dsa": "algorithms",
            "algo": "algorithms",
            "algorithm": "algorithms",
            "ml": "machine learning",
        }
        for alias, domain in alias_map.items():
            if text == alias or alias in text:
                return domain

        for domain in DOMAINS:
            if text == domain or domain in text or text in domain:
                return domain
        return None

    def _docs(self, domain: str) -> List[Dict[str, str]]:
        docs = {
            "frontend": [
                {"title": "MDN Web Docs", "url": "https://developer.mozilla.org/en-US/"},
                {"title": "React Docs", "url": "https://react.dev/"},
                {"title": "CSS Tricks", "url": "https://css-tricks.com/"},
            ],
            "backend": [
                {"title": "FastAPI Docs", "url": "https://fastapi.tiangolo.com/"},
                {"title": "Node.js Docs", "url": "https://nodejs.org/en/docs/"},
                {"title": "PostgreSQL Docs", "url": "https://www.postgresql.org/docs/"},
            ],
            "data analytics": [
                {"title": "Pandas Docs", "url": "https://pandas.pydata.org/docs/"},
                {"title": "Tableau Learning", "url": "https://www.tableau.com/learn"},
                {"title": "SQL Tutorial", "url": "https://www.w3schools.com/sql/"},
            ],
            "machine learning": [
                {"title": "Scikit-learn Docs", "url": "https://scikit-learn.org/stable/"},
                {"title": "TensorFlow Docs", "url": "https://www.tensorflow.org/learn"},
                {"title": "PyTorch Docs", "url": "https://pytorch.org/docs/stable/"},
            ],
            "devops": [
                {"title": "Docker Docs", "url": "https://docs.docker.com/"},
                {"title": "Kubernetes Docs", "url": "https://kubernetes.io/docs/"},
                {"title": "AWS Docs", "url": "https://docs.aws.amazon.com/"},
            ],
            "cybersecurity": [
                {"title": "OWASP", "url": "https://owasp.org/"},
                {"title": "NIST CSF", "url": "https://www.nist.gov/cyberframework"},
                {"title": "SANS Papers", "url": "https://www.sans.org/white-papers/"},
            ],
            "data engineering": [
                {"title": "Apache Spark Docs", "url": "https://spark.apache.org/docs/latest/"},
                {"title": "Apache Kafka Docs", "url": "https://kafka.apache.org/documentation/"},
                {"title": "Airflow Docs", "url": "https://airflow.apache.org/docs/"},
            ],
            "algorithms": [
                {"title": "LeetCode", "url": "https://leetcode.com/"},
                {"title": "GeeksforGeeks", "url": "https://www.geeksforgeeks.org/"},
                {"title": "Algorithm Visualizer", "url": "https://algorithm-visualizer.org/"},
            ],
        }
        return docs.get(domain, docs["frontend"])

    def _default_roadmap(self, domain: str) -> Dict:
        domain_docs = self._docs(domain)
        foundation_topics = DOMAIN_TOPICS[domain][:2]
        core_topics = DOMAIN_TOPICS[domain][2:4]
        advanced_topics = DOMAIN_TOPICS[domain][4:7]

        steps = [
            {
                "step": 1,
                "title": f"{domain.title()} Foundations",
                "duration": "3-4 weeks",
                "topics": foundation_topics + [
                    "core terminology and workflows",
                    "hands-on setup and environment",
                    "best practices baseline",
                ],
                "resources": [
                    domain_docs[0],
                    {"title": "Roadmap.sh", "url": "https://roadmap.sh/"},
                    {"title": "freeCodeCamp", "url": "https://www.freecodecamp.org/"},
                ],
                "projects": [
                    f"Beginner {domain} setup project",
                    f"{domain.title()} fundamentals practice notebook",
                    "Weekly concept summary and implementation log",
                ],
            },
            {
                "step": 2,
                "title": "Core Tools and Workflows",
                "duration": "4-5 weeks",
                "topics": core_topics + [
                    "tooling and debugging workflow",
                    "common mistakes and how to avoid them",
                    "documentation-first learning",
                ],
                "resources": [
                    domain_docs[1] if len(domain_docs) > 1 else domain_docs[0],
                    {"title": "GeeksforGeeks", "url": "https://www.geeksforgeeks.org/"},
                    {"title": "W3Schools", "url": "https://www.w3schools.com/"},
                ],
                "projects": [
                    f"Intermediate {domain} mini project",
                    "Debugging and optimization challenge set",
                    "Build a reusable component or utility set",
                ],
            },
            {
                "step": 3,
                "title": "Applied Practice and Real Scenarios",
                "duration": "5-6 weeks",
                "topics": [
                    advanced_topics[0],
                    "real world problem solving",
                    "testing and validation",
                    "performance fundamentals",
                    "code quality and maintainability",
                ],
                "resources": [
                    domain_docs[2] if len(domain_docs) > 2 else domain_docs[0],
                    {"title": "Kaggle", "url": "https://www.kaggle.com/"},
                    {"title": "GitHub", "url": "https://github.com/"},
                ],
                "projects": [
                    f"Case study based {domain} project",
                    "End to end feature implementation",
                    "Performance and quality audit report",
                ],
            },
            {
                "step": 4,
                "title": "Advanced Concepts",
                "duration": "5-6 weeks",
                "topics": [
                    advanced_topics[1] if len(advanced_topics) > 1 else advanced_topics[0],
                    advanced_topics[2] if len(advanced_topics) > 2 else "advanced patterns",
                    "system design thinking",
                    "scalability and reliability",
                    "security and production concerns",
                ],
                "resources": [
                    {"title": "MIT OpenCourseWare", "url": "https://ocw.mit.edu/"},
                    {"title": "Coursera", "url": "https://www.coursera.org/"},
                    {"title": "edX", "url": "https://www.edx.org/"},
                ],
                "projects": [
                    f"Advanced {domain} architecture project",
                    "Scalability improvement exercise",
                    "Production readiness checklist implementation",
                ],
            },
            {
                "step": 5,
                "title": "Portfolio Development",
                "duration": "4-5 weeks",
                "topics": [
                    "project documentation",
                    "presentation and storytelling",
                    "version control workflows",
                    "collaboration and review process",
                    "portfolio polishing",
                ],
                "resources": [
                    {"title": "GitHub Docs", "url": "https://docs.github.com/"},
                    {"title": "Dev.to", "url": "https://dev.to/"},
                    {"title": "Medium", "url": "https://medium.com/"},
                ],
                "projects": [
                    f"Flagship portfolio project in {domain}",
                    "Write a technical case study",
                    "Build a project demo and walkthrough",
                ],
            },
            {
                "step": 6,
                "title": "Career and Interview Preparation",
                "duration": "3-4 weeks",
                "topics": [
                    "resume and profile alignment",
                    "interview question practice",
                    "domain specific system/design questions",
                    "behavioral interview preparation",
                    "job application strategy",
                ],
                "resources": [
                    {"title": "InterviewBit", "url": "https://www.interviewbit.com/"},
                    {"title": "LeetCode", "url": "https://leetcode.com/"},
                    {"title": "Glassdoor", "url": "https://www.glassdoor.com/"},
                ],
                "projects": [
                    "Mock interview practice plan",
                    "Domain specific question bank",
                    "30 day job readiness tracker",
                ],
            },
        ]

        return {
            "domain": domain,
            "title": f"{domain.title()} Learning Roadmap",
            "description": f"Complete guide to becoming proficient in {domain} with structured practice and projects.",
            "prerequisites": "Basic programming fundamentals",
            "duration": "5-7 months with consistent practice",
            "steps": steps,
            "career_paths": [
                f"Junior {domain.title()} Specialist",
                f"{domain.title()} Engineer",
                "Software Engineer",
                "Consultant",
                "Technical Lead",
            ],
            "tips": [
                "Practice consistently and track what you learned every week",
                "Focus on fundamentals before moving to advanced tools",
                "Build and ship projects to convert theory into confidence",
                "Review and refactor your old work to improve quality",
                "Prepare interview explanations for each major concept",
            ],
        }

    def _recommendations(self, domain: str, score: int, total: int, level: str) -> Dict:
        percentage_value = int(round((score / total) * 100)) if total else 0
        weak_topics = [topic for topic in DOMAIN_TOPICS[domain]][score:]
        level_descriptions = {
            "Beginner": "You have a base understanding and should focus on core fundamentals.",
            "Intermediate": "You have working knowledge and should deepen practical implementation.",
            "Advanced": "You show strong capability; focus on advanced patterns and production depth.",
        }

        areas_to_improve = [
            {
                "question": f"Do you have experience with {topic}?",
                "explanation": f"Strengthen this area in {domain} through focused practice and mini projects.",
            }
            for topic in weak_topics[:3]
        ]

        if level == "Beginner":
            topics = DOMAIN_TOPICS[domain]
        elif level == "Intermediate":
            topics = DOMAIN_TOPICS[domain] + ["testing", "debugging", "best practices"]
        else:
            topics = DOMAIN_TOPICS[domain] + ["system design", "performance optimization", "production readiness"]

        return {
            "level": level,
            "domain": domain.title(),
            "score": f"{score}/{total}",
            "percentage": f"{percentage_value}%",
            "level_description": level_descriptions[level],
            "areas_to_improve": areas_to_improve,
            "explanation": f"Based on your responses, your current {domain} proficiency is {level.lower()}.",
            "topics": topics,
            "projects": DOMAIN_PROJECTS[domain],
        }

    def _topic_info(self, topic: str, domain: str) -> str:
        explanation = TOPIC_EXPLANATIONS.get(
            topic,
            "This topic is important for building a strong foundation in this domain.",
        )
        reassurance_options = [
            f"That is completely okay, not knowing {topic} yet is very normal.",
            f"No worries at all, many people in {domain} start without confidence in {topic}.",
            f"You are doing fine, it is common to feel unsure about {topic} in the beginning.",
        ]
        bridge_options = [
            f"In simple words, {explanation}",
            f"A simple way to see it is this, {explanation}",
            f"You can think of it this way, {explanation}",
        ]
        value_options = [
            f"Once this clicks, your work in {domain} becomes more structured and easier to improve.",
            f"Learning this gives you a stronger base for real {domain} tasks and problem solving.",
            f"With this concept clear, you can approach {domain} work with more confidence.",
        ]
        action_options = [
            f"For now, try one very small exercise on {topic.lower()} and keep it simple.",
            f"A good next step is to practice one beginner level example of {topic.lower()} today.",
            f"Start with a tiny hands on task around {topic.lower()} and build from there.",
        ]

        return "\n".join(
            [
                random.choice(reassurance_options),
                random.choice(bridge_options),
                random.choice(value_options),
                random.choice(action_options),
            ]
        )
