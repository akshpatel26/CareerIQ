JOB_ROLES = {
    "Software Development and Engineering": {
      "Frontend Developer": {
        "required_skills": [
          "HTML", "CSS", "JavaScript", "React", "Angular", "Vue.js", "TypeScript",
          "Responsive Design", "Git", "Version Control"
        ],
        "description": "Create user interfaces and implement visual elements",
        "sections": ["Technical Skills", "Projects", "Professional Experience", "Education"],
        "recommended_skills": {
          "technical": [
            "HTML", "CSS", "JavaScript", "React.js", "Angular", "Vue.js", "TypeScript", "Git",
            "Responsive Design", "Bootstrap", "Tailwind CSS"
          ],
          "soft": ["Communication", "Problem-solving", "Attention to detail", "Creativity"]
        }
      },
      "Backend Developer": {
        "required_skills": [
          "Python", "Java", "Node.js", "SQL", "REST APIs", "Django", "Flask", "MongoDB",
          "Database Design", "SQLAlchemy", "Hibernate", "Postman"
        ],
        "description": "Build server-side logic and databases",
        "sections": ["Technical Skills", "System Architecture", "Professional Experience", "Education"],
        "recommended_skills": {
          "technical": [
            "Python", "Java", "Node.js", "SQL", "RESTful APIs", "Microservices",
            "Docker", "SQLAlchemy", "Hibernate", "AWS", "Azure"
          ],
          "soft": ["Analytical thinking", "Problem-solving", "Team collaboration"]
        }
      },
      "Full Stack Developer": {
        "required_skills": [
          "HTML", "CSS", "JavaScript", "React", "Angular", "Python", "Java", "Node.js",
          "MERN Stack", "MongoDB", "Express.js", "REST APIs", "SQL"
        ],
        "description": "Handle both client and server-side development",
        "sections": ["Technical Skills", "Full Stack Projects", "Professional Experience", "Education"],
        "recommended_skills": {
          "technical": [
            "React", "Angular", "Vue.js", "Django", "Express", "SQL", "NoSQL",
            "API Development", "Docker", "Kubernetes", "AWS", "Azure"
          ],
          "soft": ["Versatility", "Project management", "Communication"]
        }
      },
      "Mobile App Developer": {
        "required_skills": [
          "Swift", "Kotlin", "React Native", "Flutter", "Mobile UI/UX", "App Store",
          "Cross-platform Development", "Performance Optimization"
        ],
        "description": "Develop mobile applications for iOS and Android",
        "sections": ["Technical Skills", "Mobile Projects", "Professional Experience", "Education"],
        "recommended_skills": {
          "technical": [
            "Swift", "Xcode", "Kotlin", "Android Studio", "React Native", "Flutter", "Mobile UI/UX"
          ],
          "soft": ["User-centric thinking", "Problem-solving", "Attention to detail"]
        }
      }
    },
    "Data Science and Analytics": {
      "Data Scientist": {
        "required_skills": [
          "Python", "R", "Machine Learning", "Statistics", "SQL", "Deep Learning",
          "Data Cleaning", "Feature Engineering", "Hadoop", "Spark", "Matplotlib", "Seaborn"
        ],
        "description": "Analyze complex data sets to find patterns",
        "sections": ["Technical Skills", "Projects", "Research", "Education"],
        "recommended_skills": {
          "technical": [
            "Python", "R", "Machine Learning", "Statistics", "Big Data",
            "Data Visualization", "TensorFlow", "PyTorch"
          ],
          "soft": ["Analytical thinking", "Research", "Problem-solving"]
        }
      },
      "Data Analyst": {
        "required_skills": [
          "SQL", "Excel", "Python", "Data Visualization", "Statistics",
          "Tableau", "Power BI", "NumPy", "Pandas", "Matplotlib", "Seaborn"
        ],
        "description": "Transform data into insights",
        "sections": ["Technical Skills", "Analysis Projects", "Professional Experience", "Education"],
        "recommended_skills": {
          "technical": [
            "SQL", "Excel", "Python", "Tableau", "Power BI", "Statistical Analysis"
          ],
          "soft": ["Data interpretation", "Communication", "Attention to detail"]
        }
      },
      "Machine Learning Engineer": {
        "required_skills": [
          "Python", "TensorFlow", "Deep Learning", "Model Deployment", "scikit-learn",
          "Streamlit", "NumPy", "Pandas", "Matplotlib", "Supervised Learning", "Unsupervised Learning"
        ],
        "description": "Build and deploy machine learning models",
        "sections": ["Technical Skills", "ML Projects", "Professional Experience", "Education"],
        "recommended_skills": {
          "technical": [
            "Machine Learning", "Deep Learning", "MLOps", "Model Deployment", "Cloud ML"
          ],
          "soft": ["Research", "Problem-solving", "Critical thinking"]
        }
      }
    },
    "Cloud Computing and DevOps": {
      "Cloud Architect": {
        "required_skills": [
          "AWS", "Azure", "GCP", "Terraform", "CloudFormation",
          "Security", "Networking", "Cost Optimization", "Compliance"
        ],
        "description": "Design and manage cloud infrastructure",
        "sections": ["Technical Skills", "Cloud Projects", "Professional Experience", "Certifications"],
        "recommended_skills": {
          "technical": [
            "AWS", "Azure", "GCP", "Security", "Networking", "Infrastructure as Code"
          ],
          "soft": ["Strategic thinking", "Problem-solving", "Communication"]
        }
      },
      "DevOps Engineer": {
        "required_skills": [
          "Docker", "Kubernetes", "CI/CD", "Automation", "Monitoring",
          "Python", "Bash", "Infrastructure as Code", "Jenkins", "Git"
        ],
        "description": "Implement DevOps practices and tools",
        "sections": ["Technical Skills", "DevOps Projects", "Professional Experience", "Education"],
        "recommended_skills": {
          "technical": [
            "Docker", "Kubernetes", "CI/CD", "Infrastructure as Code",
            "Prometheus", "Grafana", "Jenkins"
          ],
          "soft": ["Automation mindset", "Problem-solving", "Team collaboration"]
        }
      }
    },
    "Cybersecurity": {
      "Security Analyst": {
        "required_skills": [
          "Network Security", "Threat Detection", "SIEM", "Splunk", "QRadar",
          "Incident Response", "ISO", "GDPR", "Compliance"
        ],
        "description": "Monitor and protect against security threats",
        "sections": ["Technical Skills", "Security Projects", "Professional Experience", "Certifications"],
        "recommended_skills": {
          "technical": [
            "Security Tools", "Threat Analysis", "Incident Response", "Compliance"
          ],
          "soft": ["Analytical thinking", "Attention to detail", "Communication"]
        }
      },
      "Penetration Tester": {
        "required_skills": [
          "Ethical Hacking", "Burp Suite", "Metasploit", "Network Security", "Web Security",
          "Vulnerability Assessment", "CEH", "OSCP"
        ],
        "description": "Test systems for security vulnerabilities",
        "sections": ["Technical Skills", "Security Projects", "Professional Experience", "Certifications"],
        "recommended_skills": {
          "technical": [
            "Penetration Testing", "Security Tools", "Vulnerability Assessment"
          ],
          "soft": ["Ethical mindset", "Problem-solving", "Report writing"]
        }
      }
    },
    "UI/UX Design": {
      "UI Designer": {
        "required_skills": [
          "Figma", "Adobe XD", "Visual Design", "Typography", "Color Theory",
          "Design Systems", "Prototyping", "Accessibility"
        ],
        "description": "Create beautiful user interfaces",
        "sections": ["Design Skills", "Portfolio", "Professional Experience", "Education"],
        "recommended_skills": {
          "technical": [
            "Figma", "Adobe XD", "Visual Design", "Prototyping", "Design Systems"
          ],
          "soft": ["Creativity", "Attention to detail", "User empathy"]
        }
      },
      "UX Designer": {
        "required_skills": [
          "User Research", "Wireframing", "Prototyping", "Usability Testing",
          "Research Methods", "Information Architecture", "Google Analytics"
        ],
        "description": "Design user experiences and flows",
        "sections": ["Design Skills", "Case Studies", "Professional Experience", "Education"],
        "recommended_skills": {
          "technical": [
            "User Research", "Information Architecture", "User Testing", "Analytics"
          ],
          "soft": ["Empathy", "Communication", "Problem-solving"]
        }
      }
    },
    "Project Management": {
      "Project Manager": {
        "required_skills": [
          "Project Planning", "Agile", "Scrum", "Risk Management", "Stakeholder Management",
          "JIRA", "MS Project", "Budgeting", "CSM"
        ],
        "description": "Lead and manage project delivery",
        "sections": ["Management Skills", "Project History", "Professional Experience", "Certifications"],
        "recommended_skills": {
          "technical": [
            "Project Management", "Agile", "Scrum", "JIRA", "Budgeting"
          ],
          "soft": ["Leadership", "Communication", "Problem-solving"]
        }
      },
      "Product Manager": {
        "required_skills": [
          "Product Strategy", "Market Research", "User Stories", "Roadmapping",
          "Product Management", "Analytics", "A/B Testing"
        ],
        "description": "Define and drive product vision",
        "sections": ["Product Skills", "Product Launches", "Professional Experience", "Education"],
        "recommended_skills": {
          "technical": [
            "Product Management", "Analytics", "Market Research", "A/B Testing"
          ],
          "soft": ["Strategic thinking", "Communication", "Leadership"]
        }
      }
    }
}