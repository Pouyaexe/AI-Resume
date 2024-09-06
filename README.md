### AI-Resume: Intelligent Resume Rewriting Using Harvard Guidelines

---

AI-Resume is an intelligent resume rewriting tool designed to enhance and optimize resumes based on Harvard's professional guidelines. Leveraging state-of-the-art technologies such as **_Streamlit_** for the interactive user interface, **_LangChain_** for building advanced text retrieval and rewriting pipelines, and **_FAISS_** for efficient similarity search, AI-Resume transforms standard resumes into polished, professional documents. The application uses **_Google Generative AI_** models for natural language processing, **_HuggingFace Embeddings_** for turning text into searchable vectors, and **_pdfplumber_** for accurate PDF text extraction. By integrating **_python-docx_** for document formatting, the app provides users with the ability to download their improved resumes in both **_Markdown_** and **_DOCX_** formats, ensuring ease of use across platforms. With seamless modularization, AI-Resume delivers a comprehensive solution for resume improvement, simplifying job application processes.

[Check out the Live Demo](https://ai-resume-rewrite.streamlit.app/)

![AI-Resume Banner](./assets/Robot-resume.png)

---

### Pipeline Overview

The AI-Resume tool follows a modular pipeline that consists of several stages, each with its own responsibility. This ensures a clear separation of concerns and allows flexibility in improving or replacing individual components. Here's a high-level view of the pipeline:

1. **PDF Extraction**: The user's resume in PDF format is parsed to extract raw text, which is then cleaned and organized into meaningful sections such as *Education*, *Work Experience*, *Skills*, and *Hobbies*.
2. **Guideline Retrieval**: Harvard's resume guidelines are stored in a Markdown file and used as reference data to guide the improvements for each resume section.
3. **Embedding Creation**: The guidelines are split into text chunks and vectorized (converted into numerical embeddings) using pre-trained models. This allows the app to search for the most relevant sections from the guideline for each part of the user’s resume.
4. **Feedback and Rewrite Generation**: Using Google’s Gemini AI, feedback is generated for each section of the resume. Afterward, each section is rewritten based on both the guidelines and feedback.
5. **Resume Reconstruction**: The feedback is shown to the user, and the fully rewritten resume is provided in Markdown and DOCX formats for download.

---

### Detailed Walkthrough of Key Components

#### 1. **PDF Parsing and Cleaning**

The first step in the pipeline is the extraction of text from a PDF resume. The `pdf_utils.py` file contains two important functions:

- **`extract_pdf_text(uploaded_file)`**: This function uses the `pdfplumber` library to extract raw text from the uploaded PDF. Each page of the PDF is processed to gather all textual data.
- **`clean_extracted_text(raw_text)`**: Once the text is extracted, this function is responsible for cleaning the raw text. This includes removing extra line breaks, fixing spacing issues, and ensuring that the text can be processed easily in the next steps.

  **Process**:
- The resume text is parsed into sections based on natural headers (e.g., "Education", "Work Experience"). A regex-based approach detects where one section ends, and another begins.

#### 2. **Harvard Guideline Retrieval**

The next step is to retrieve the relevant guidelines to assist in improving each resume section. The app stores Harvard resume guidelines in a Markdown file (`assets/harvard_resume_guide.md`).

- **Guideline Chunking**: The guideline content is split into small, meaningful chunks using the `split_text()` function from `vectorstore_utils.py`. Each chunk contains information about a specific section of the resume guidelines (e.g., how to write an impactful "Work Experience" section).
- **Creating a Vector Store**: The vector store (created using FAISS) indexes these chunks. Each chunk is vectorized using HuggingFace’s sentence-transformer model, allowing for efficient similarity searches later in the process. This vectorization helps retrieve the most relevant guideline sections for any part of the user’s resume.

#### 3. **Data Retrieval and Querying**

After organizing the guideline data into chunks and vectorizing them, the app uses a *Retrieval-Augmented Generation (RAG)* pipeline to process the user’s resume and retrieve the most relevant guideline information. Here’s how the RAG pipeline works:

- **Embedding-based Retrieval**: Each section of the user’s resume (e.g., "Education") is compared against the vectorized chunks of the guidelines using FAISS similarity search. The app searches for the most similar guideline content by comparing the vectorized representations of both the resume text and guideline chunks.
- **Chains for Feedback and Rewriting**: Two separate chains are used to process the resume:

  - **Feedback Chain**: The feedback chain generates feedback for each resume section, explaining how it could be improved (e.g., adding more quantified achievements, using active language).
  - **Rewrite Chain**: The rewrite chain takes the feedback, the guidelines, and the original resume section, and generates an improved version of the section.

  The LLM pipeline, implemented in `llm_pipeline.py`, handles the setup of these chains. It defines how the model retrieves data and how the resume sections are rewritten.

#### 4. **Resume Section Processing**

   The `process_resume()` function in `resume_parser.py` manages how each section of the resume is processed. It works in two stages:

- **Retrieving Relevant Guidelines**: For each section (e.g., "Skills"), the app queries the vector store for the most relevant guidance. This query returns several guideline chunks (e.g., how to describe technical skills, how to quantify achievements).
- **Generating Feedback and Rewriting**: Once the guidelines are retrieved, the app sends this information, along with the original section text, to the feedback and rewrite chains. The feedback explains what’s wrong or missing, and the rewrite generates a professional version.
- **Handling Full Resume Rewrite**: In addition to section-by-section rewriting, the app uses the `process_full_resume()` function, which passes the entire resume and feedback to the LLM, asking it to generate a complete, professional version of the resume in one go.

#### 5. **User Interface (UI)**

The user interface is designed with simplicity and interactivity in mind. Users upload their resumes, get feedback, and download rewritten resumes in various formats. The UI is built using Streamlit and modularized in `ui_components.py` to ensure clean code and easy maintenance.

- **Resume Upload and Display**: Users upload resumes in PDF format. The app then displays the extracted resume and feedback in separate sections.
- **Copy to Clipboard**: The `st_copy_to_clipboard` feature allows users to easily copy the markdown version of the resume for use in other platforms.
- **Download Options**: Users can download the resume in Markdown or DOCX formats. Markdown allows flexibility, while DOCX provides a professional format.

#### 6. **Markdown to DOCX Conversion**

The module `markdown_to_docx.py` handles the conversion from markdown to DOCX format. It uses `BeautifulSoup` to parse the HTML generated from the markdown and the `python-docx` library to convert the parsed HTML elements into a Word document.

- **Text Formatting**: Markdown elements like bold (`**bold**`), italic (`*italic*`), and headings are translated into their corresponding DOCX formats.
- **Lists and Bullet Points**: Unordered lists and bullet points are also supported, allowing for the proper rendering of resume sections like "Skills" and "Experience."

#### 7. **File Management and Downloads**

- **File Conversion**: The app saves the Markdown resume to a file (`full_resume.md`) and converts it to DOCX using the `convert_markdown_to_docx()` function. The DOCX file is stored temporarily and provided to the user for download.
- **Download Handling**: The `BytesIO` buffer is used to manage the DOCX content in memory, making the download process efficient without the need for temporary file storage on disk.

---

### Advanced Capabilities and Thought Process

#### **Embedding-Based Retrieval**:

The key strength of AI-Resume lies in its ability to efficiently retrieve relevant guideline sections using FAISS (Facebook AI Similarity Search). This enables the model to provide personalized, section-specific feedback based on the actual content of the user's resume. By vectorizing both the resume and the guidelines using sentence transformers, the app can match user text with relevant guidance even if the wording or phrasing differs.

#### **Modularized Rewriting**:

By breaking the resume into sections and processing each section separately, the app ensures that every part of the resume receives personalized attention. This approach allows for more control over each section, with specific feedback provided for the "Education", "Work Experience", and "Skills" sections, among others. The modular approach also enables easy debugging and improvements since the app can focus on specific sections independently.

#### **Full Resume Synthesis**:

Once individual sections are improved, the full resume is reconstructed into a cohesive, well-formatted document. By providing both a section-by-section rewrite and a full resume rewrite, the app empowers users to choose the version that best meets their needs.

#### **Professional Formatting**:

In addition to feedback and rewriting, **AI-Resume** focuses on generating professional-grade outputs in both Markdown and DOCX formats. The use of the `python-docx` library ensures that the rewritten resume is delivered in a format that is ready for job applications, without the need for additional formatting by the user.

---

### Summary

**AI-Resume** showcases how cutting-edge AI models, data retrieval techniques, and seamless integration with user-friendly interfaces can revolutionize everyday tasks such as resume writing. By making professional resume rewriting accessible and efficient, the app empowers job seekers to present their qualifications in the best possible light.

From the robust PDF text extraction process to the modular LangChain-based rewriting pipeline, AI-Resume combines advanced techniques to deliver a highly functional, intuitive, and valuable tool.
