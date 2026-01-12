class PratikProfile:
    def __init__(self):
        self.name = "Pratik Raj(プラティク・ラージ)"
        self.education = {
            "degree": "Bachelor of Technology in Data Science",
            "institution": "no information",
            "expected_graduation": "May 2027"
        }
        
        self.educational_background = [
            {"level": "Higher Secondary Education (Class 12)", "percentage": "75.6%", "year": "2022"},
            {"level": "Secondary Education (Class 10)", "percentage": "88%", "year": "2020"}
        ]
        
        self.technical_skills = {
            "languages": ["Python", "SQL", "Java", "JavaScript", "HTML/CSS"],
            "ai_ml_frameworks": ["TensorFlow", "PyTorch", "Scikit-learn", "Hugging Face", "LangChain", "Ollama"],
            "web_technologies": ["Flask", "Streamlit", "Gradio", "FastAPI", "REST APIs"],
            "databases_tools": ["Supabase", "MySQL", "Git", "GitHub", "Docker", "Render"],
            "core_competencies": ["Machine Learning", "NLP", "RAG Systems", "Data Structures & Algorithms", "Prompt Engineering", "Data Visualization"]
        }
        
        self.projects = [
            {
                "name": "RAG Knowledge Agent",
                "technologies": ["Flask", "Supabase", "Ollama", "Vector DB", "HTML/CSS/JS"],
                "period": "Oct 2024",
                "description": "Full-stack web app with multi-modal AI capabilities including document-based RAG, general LLM queries, and real-time web search integration."
            },
            {
                "name": "AI Financial Analyst",
                "technologies": ["Python", "Streamlit", "OpenRouter API", "Ollama", "Data Visualization"],
                "period": "Sept 2024",
                "description": "Automated financial analysis platform leveraging multiple LLM backends for diverse analytical perspectives."
            },
            {
                "name": "Prompt Structurer & Analyzer",
                "technologies": ["Python", "Streamlit", "OpenRouter", "Ollama", "Mermaid.js"],
                "period": "Aug 2024",
                "description": "Tool to transform natural language into structured JSON/YAML prompts, reducing AI hallucinations by 40%."
            }
        ]
        
        self.competitive_programming = {
            "leetcode_profile": {
                "problems_solved": 216,
                "breakdown": {"Easy": 144, "Medium": 68, "Hard": 4},
                "max_streak": 261,
                "global_rank": 651216
            }
        }
        
        self.certifications = [
            {"name": "Oracle Generative AI Professional Certificate", "description": "Comprehensive training in GenAI architectures"},
            {"name": "Hugging Face NLP Specialization", "description": "Advanced NLP and transformer models"},
            {"name": "Hacktoberfest Contributor", "description": "Active open-source contributor"}
        ]
    
    def get_profile_summary(self):
        skills = ", ".join(self.technical_skills['languages'] + self.technical_skills['ai_ml_frameworks'][:3])
        projects = ", ".join([p['name'] for p in self.projects])
        return f"{self.name} - AI/ML Engineer & Data Science Student. Skills: {skills}. Projects: {projects}. LeetCode: {self.competitive_programming['leetcode_profile']['problems_solved']} problems solved."

pratik_profile = PratikProfile()

def get_pratik_context():
    return pratik_profile.get_profile_summary()