"""
Pratik Raj - AI/ML Engineer & Data Science Student
Profile Summary for AI Assistant Context
"""

# Personal Profile (excluding personal contact details)
class PratikProfile:
    def __init__(self):
        self.name = "Pratik Raj(プラティク・ラージ)"
        self.education = {
            "degree": "Bachelor of Technology in Data Science",
            "institution": "no information",  # Institution name kept as it's part of his professional background
            "expected_graduation": "May 2027"
        }
        
        self.educational_background = [
            {
                "level": "Higher Secondary Education (Class 12)",
                "percentage": "75.6%",
                "year": "2022"
            },
            {
                "level": "Secondary Education (Class 10)", 
                "percentage": "88%",
                "year": "2020"
            }
        ]
        
        self.technical_skills = {
            "languages": ["Python", "SQL", "Java", "JavaScript", "HTML/CSS"],
            "ai_ml_frameworks": ["TensorFlow", "PyTorch", "Scikit-learn", "Hugging Face", "LangChain", "Ollama"],
            "web_technologies": ["Flask", "Streamlit", "Gradio", "FastAPI", "REST APIs"],
            "databases_tools": ["Supabase", "MySQL", "Git", "GitHub", "Docker", "Render"],
            "core_competencies": ["Machine Learning", "NLP", "RAG Systems", "Data Structures & Algorithms", 
                                "Prompt Engineering", "Data Visualization"]
        }
        
        self.projects = [
            {
                "name": "RAG Knowledge Agent",
                "technologies": ["Flask", "Supabase", "Ollama", "Vector DB", "HTML/CSS/JS"],
                "period": "Oct 2024",
                "description": "Built full-stack web application with multi-modal AI capabilities including document-based RAG, "
                             "general LLM queries, and real-time web search integration. Engineered PDF document processing "
                             "pipeline with vector embeddings stored in Supabase for semantic search. Implemented "
                             "context-aware QA system with streaming responses and glassmorphism UI, improving user "
                             "engagement by providing real-time feedback during query processing."
            },
            {
                "name": "AI Financial Analyst",
                "technologies": ["Python", "Streamlit", "OpenRouter API", "Ollama", "Data Visualization"],
                "period": "Sept 2024",
                "description": "Developed automated financial analysis platform leveraging multiple LLM backends for "
                             "diverse analytical perspectives. Created interactive dashboards with dynamic chart "
                             "generation and web-scraping capabilities for real-time financial data. Integrated "
                             "OpenRouter and Ollama APIs to enable comparative analysis across different AI models, "
                             "enhancing decision-making quality."
            },
            {
                "name": "Prompt Structurer & Analyzer",
                "technologies": ["Python", "Streamlit", "OpenRouter", "Ollama", "Mermaid.js"],
                "period": "Aug 2024",
                "description": "Designed tool to transform natural language into structured JSON/YAML prompts, "
                             "reducing AI hallucinations by 40%. Built side-by-side testing interface with quality "
                             "scoring metrics and token cost tracking for optimization. Implemented smart "
                             "restructuring algorithms with format conversion capabilities, improving prompt "
                             "clarity and response accuracy."
            }
        ]
        
        self.competitive_programming = {
            "leetcode_profile": {
                "problems_solved": 216,
                "breakdown": {"Easy": 144, "Medium": 68, "Hard": 4},
                "max_streak": 261,
                "global_rank": 651216
            },
            "problem_solving_strengths": "Strong foundation in algorithms and data structures with consistent "
                                       "practice across multiple languages (Python, SQL, Java)"
        }
        
        self.certifications = [
            {
                "name": "Oracle Generative AI Professional Certificate",
                "description": "Comprehensive training in GenAI architectures and applications"
            },
            {
                "name": "Hugging Face NLP Specialization", 
                "description": "Advanced natural language processing and transformer models"
            },
            {
                "name": "Hacktoberfest Contributor",
                "description": "Active open-source contributor with merged pull requests"
            }
        ]
    
    def get_profile_summary(self):
        """Return a comprehensive summary of Pratik's profile"""
        summary = f"""
{self.name} - AI/ML Engineer & Data Science Student

Education:
- {self.education['degree']} ({self.education['expected_graduation']})
- Educational Background: {len(self.educational_background)} levels

Technical Skills:
- Languages: {', '.join(self.technical_skills['languages'])}
- AI/ML Frameworks: {', '.join(self.technical_skills['ai_ml_frameworks'])}
- Web Technologies: {', '.join(self.technical_skills['web_technologies'])}
- Databases & Tools: {', '.join(self.technical_skills['databases_tools'])}
- Core Competencies: {', '.join(self.technical_skills['core_competencies'])}

Projects:
{self._format_projects()}

Competitive Programming:
- LeetCode: {self.competitive_programming['leetcode_profile']['problems_solved']} problems solved 
  ({self.competitive_programming['leetcode_profile']['breakdown']['Easy']} Easy, 
   {self.competitive_programming['leetcode_profile']['breakdown']['Medium']} Medium, 
   {self.competitive_programming['leetcode_profile']['breakdown']['Hard']} Hard)
- Max Streak: {self.competitive_programming['leetcode_profile']['max_streak']} days
- Global Rank: {self.competitive_programming['leetcode_profile']['global_rank']}

Certifications:
{self._format_certifications()}
        """
        return summary
    
    def _format_projects(self):
        """Format projects for display"""
        formatted = []
        for project in self.projects:
            formatted.append(f"- {project['name']} ({project['period']}): {project['description'][:100]}...")
        return '\n'.join(formatted)
    
    def _format_certifications(self):
        """Format certifications for display"""
        formatted = []
        for cert in self.certifications:
            formatted.append(f"- {cert['name']}: {cert['description']}")
        return '\n'.join(formatted)


# Create instance of Pratik's profile
pratik_profile = PratikProfile()

# Define a function to get Pratik's profile information for AI context
def get_pratik_context():
    """
    Returns Pratik's professional profile information for use as context in AI conversations.
    This provides background information about Pratik's skills, projects, and expertise.
    """
    return pratik_profile.get_profile_summary()


# If this file is run directly, print the profile summary
if __name__ == "__main__":
    print(get_pratik_context())