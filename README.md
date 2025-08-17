
<p><small>Best View in <a href="https://github.com/settings/appearance">Dark Mode</a> (Recommended)</small></p><br/>



#  **🏝️ Smart AI Resume Analyzer 🏝️**  
<!--<img src="https://github.com/user-attachments/assets/8a37c282-efa0-45af-8f37-8e564a62ecd2" width="35">-->
 Smart AI Resume Analyzer is your all-in-one tool to analyze, optimize, and craft resumes that stand out, helping you land your dream job.  
</div>

  
## <img src="https://github.com/user-attachments/assets/a6e4d77f-56d6-4aa8-8278-0f5a18ef5eb9" width="24px"> **What Makes Us Different?**  

**<img src="https://github.com/user-attachments/assets/76906dbc-343d-4267-ace5-048d428fff42" width="20px"> Next-Level Features for Success:**  
1. 🎨 **AI-Powered Resume Builder:**  
   - **Themes that Shine** (Modern, Minimal, Professional, Creative)  
   - **Smart Content Suggestions**  
   - **ATS-Optimized Formatting**  
   - **Customizable Sections**


2. 🕵️ **Deep Resume Analysis:**  
   - 🛡️ ATS Compatibility Score  
   - 🔑 Keyword Gap Analysis  
   - 🧩 Role-specific Feedback  
   - 📊 Skills Gap Breakdown  

3. 💼 **Job Application Portal:**  
   - 🔍 Multi-Portal Search (Naukri, Indeed, Glassdoor, LinkedIn)  
   - 🤖 AI Match Score + Custom Cover Letter  
   - 🌐 LinkedIn Scraper → Direct Job Fetch & Role-Specific Cover Letter  
   - 📊 Job Market Insights (Skills, Locations, Salaries, Companies)  

4. 🧮 **Smart Quiz:**
   - 🤖 AI-Generated Quizzes
   - ⚡ Flexible Customization
   - 🔄 Adaptive Practice
   - 🎯 Wide Coverage
  

## <img src="https://github.com/user-attachments/assets/e5ac1371-6ac4-48b6-b95c-5ef9afaf1353" width="30"> **Live Demo**  
👨‍💻 Try it Now: [![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://resumind.streamlit.app/)  


## <img src="https://github.com/user-attachments/assets/0cefad05-58a9-4aa0-a070-f75a0c9b0353" height="32px">  Tech Stack 
<details>
  <summary>🌐 Frontend</summary>

| **🌟 Technology**    | **💼 Role**                                                             |  
|-----------------------|-------------------------------------------------------------------------|  
| [**Streamlit**](https://streamlit.io/)   | Builds interactive and user-friendly web apps for resume analysis.     |  
| [**HTML**](https://developer.mozilla.org/en-US/docs/Learn/HTML)  | Provides the basic structure for web pages.                             |  
| [**CSS**](https://developer.mozilla.org/en-US/docs/Web/CSS)      | Adds styling and layouts to the frontend.                               |  
| [**JavaScript**](https://developer.mozilla.org/en-US/docs/Learn/JavaScript) | Enables interactivity and dynamic behavior for the web pages.          |  

</details>

<details>
  <summary>⚙️ Backend</summary>

| **🌟 Technology**    | **💼 Role**                                                             |  
|-----------------------|-------------------------------------------------------------------------|  
| [**Streamlit**](https://streamlit.io/)   | Handles backend logic and integrates machine learning models.           |  
| [**Python**](https://www.python.org/)    | Provides core programming language for implementing functionalities.    |  

</details>

<details>
  <summary>🗄️ Database</summary>

| **🌟 Technology**    | **💼 Role**                                                             |  
|-----------------------|-------------------------------------------------------------------------|  
| [**SQLite3**](https://www.sqlite.org/index.html) | Stores and retrieves resume data for efficient processing.             |  

</details>

<details>
  <summary>📦 Modules</summary>

| **🌟 Technology**    | **💼 Role**                                                             |  
|-----------------------|-------------------------------------------------------------------------|  
| [**spaCy**](https://spacy.io/)          | Enhances NLP for keyword analysis and ATS compatibility checks.        |  
| [**Python-docx**](https://python-docx.readthedocs.io/en/latest/)    | Enables Word document editing for resume customization.                |  
| [**PyPDF2**](https://pypdf2.readthedocs.io/en/latest/)         | Processes PDF files for extracting and analyzing resumes.              |  
| [**scikit-learn**](https://scikit-learn.org/)   | Drives machine learning models for resume optimization.                |  
| [**Plotly**](https://plotly.com/)         | Creates interactive charts for skills gap and keyword analysis.        |  
| [**NLTK**](https://www.nltk.org/)         | Provides tools for tokenization, stemming, and text preprocessing in NLP. |  
| [**openpyxl**](https://openpyxl.readthedocs.io/en/stable/)      | Facilitates reading, writing, and modifying Excel files for data visualization and export. |  

</details>


## 💡 **How It Works**  

1. **Upload or Start from Scratch**  
   - Import your resume in **PDF/Word** or create one from scratch with our AI-powered builder.  

2. **Analyze Your Resume**  
   - **ATS Compatibility**: Ensure your resume meets recruiter expectations.  
   - **Keyword Insights**: Find and fill gaps in your content.  
   - **Skills Gap Analysis**: Discover key skills missing for your target role.  

3. **Build a Stunning Resume**  
   - Select from **4 unique templates** and customize sections like skills, achievements, or hobbies.  

4. **Download & Apply**  
   - Export your resume in **PDF** format, ready for submission.  This project has evolved with significant enhancements to its resume analysis capabilities:

5. **Job Application Portal**  
   - Aggregates jobs from Naukri, Indeed, Glassdoor, and LinkedIn, ranks them by AI match score, and generates personalized cover letters. LinkedIn Scraper pulls targeted jobs with match % + AI cover letters for quick applications.
 
6. **Smart Quiz**  
   - Flexible Modes → Choose from curated Question Bank quizzes (Aptitude, Reasoning, Programming, DSA, Languages) or AI-generated sets (Numerical, Logic, Reasoning, Mock Tests, etc ).
   - Smart Features → Customize #questions & timers, get detailed results with explanations, and retry or generate new quizzes instantly.


#### ✅ Step-by-Step:

1. **Create a `.env` file**.
2. **Paste your Google Gemini API key** in the following format:

#### 📄 Example content for `.env`:
```env
GOOGLE_API_KEY=your_google_gemini_api_key
```

#### <img src="https://assets.codepen.io/1468070/Google+G+Icon.png" alt="Google LOGO" width="1.6%" /> Get your Gemini API Key:
Visit  **[Google AI Studio – Gemini API Access](https://aistudio.google.com/app/apikey)** 👉 Grab and use your **own API key** — Since Mine One Have Usage Limits.


6. **Run the application:**

Start the application using Streamlit:

   ```bash
   streamlit run app.py
   ```

<details>
  <summary>📁 Folder Structure After Adding <code>.env</code></summary>

> 🔐 **Important:**  
> - **Do not commit your `.env` file** to version control (e.g., GitHub). It should be listed in `.gitignore`.
> - If you're collaborating, you can provide a safe `.env.example` file with dummy data.

  <div align="center">  
    <table>
      <tr>
        <td align="center"><b>🗂️ Folder Structure Preview 1</b></td>
        <td align="center"><b>🗂️ Folder Structure Preview 2</b></td>
      </tr>
      <tr>
        <td>
         <img width="293" height="312" alt="Screenshot 2025-08-17 114205" src="https://github.com/user-attachments/assets/a97e4311-4f5e-4fef-94af-f6287377603d" />

 </td>
        <td>
          <img width="243" height="789" alt="Screenshot 2025-08-17 105256" src="https://github.com/user-attachments/assets/de811c0a-d328-4d54-884b-189df055d42f" />

  </div>
  

</details>
   
