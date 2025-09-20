import { useState } from 'react';
import './App.css';
import Tabs from './components/Tabs';
import SkillForm from './components/SkillForm';
import JobSuggestions from './components/JobSuggestions';
import SkillGapResults from './components/SkillGapResults'; // Import the new results component

function App() {
  // State to manage which tab is active
  const [activeTab, setActiveTab] = useState('jobSuggestions');

  // V1 State: Skill Gap Analysis
  const [v1Skills, setV1Skills] = useState('');
  const [v1JobTitle, setV1JobTitle] = useState('');
  const [v1Result, setV1Result] = useState(null);

  // V2 State: Job Suggestions
  const [resumeFile, setResumeFile] = useState(null);
  const [v2Result, setV2Result] = useState(null);
  
  // Shared State
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const API_URL = ""; // For the final single-server setup

  // --- V1 API Handler ---
  const handleV1Submit = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    setError(null);
    setV1Result(null);
    
    try {
      const response = await fetch(`${API_URL}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          skills: v1Skills.split(',').map(s => s.trim()),
          job_title: v1JobTitle,
        }),
      });
      if (!response.ok) throw new Error('Skill analysis failed. Please try again.');
      const data = await response.json();
      setV1Result(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // --- V2 API Handler ---
  const handleV2Submit = async () => {
    if (!resumeFile) return setError("Please select a resume file to upload.");
    setIsLoading(true);
    setError(null);
    setV2Result(null);

    const formData = new FormData();
    formData.append("resume_file", resumeFile);

    try {
      const response = await fetch(`${API_URL}/api/suggest-jobs`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error('Job suggestion failed. Please try again.');
      const data = await response.json();
      setV2Result(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <h1>AI Career Advisor</h1>
      <Tabs activeTab={activeTab} setActiveTab={setActiveTab} />
      
      {/* Conditionally render the correct form based on the active tab */}
      {activeTab === 'gapAnalysis' && (
        <SkillForm
          skills={v1Skills}
          setSkills={setV1Skills}
          jobTitle={v1JobTitle}
          setJobTitle={setV1JobTitle}
          onSubmit={handleV1Submit}
        />
      )}
      
      {activeTab === 'jobSuggestions' && (
        <div className="form-container">
          <div className="input-group">
            <label htmlFor="resume">Upload Your Resume (PDF or DOCX)</label>
            <input type="file" id="resume" accept=".pdf,.docx" onChange={(e) => setResumeFile(e.target.files[0])} />
          </div>
          <button className="analyze-button" onClick={handleV2Submit} disabled={isLoading}>
            {isLoading ? "Analyzing..." : "Suggest Jobs"}
          </button>
        </div>
      )}
      
      {/* Display Loading and Error Messages */}
      {isLoading && <p>Analyzing...</p>}
      {error && <p className="error-message">{error}</p>}
      
      {/* Conditionally render the correct results */}
      {v1Result && activeTab === 'gapAnalysis' && (
        <SkillGapResults result={v1Result} />
      )}
      
      {v2Result && activeTab === 'jobSuggestions' && (
        <JobSuggestions suggestions={v2Result.suggestions} apiUrl={API_URL} />
      )}
    </>
  );
}

export default App;