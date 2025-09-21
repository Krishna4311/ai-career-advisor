import { useState } from 'react';

import Tabs from '../components/Tabs';
import SkillForm from '../components/SkillForm';
import JobSuggestions from '../components/JobSuggestions';
import SkillGapResults from '../components/SkillGapResults';
import CareerPathDisplay from '../components/CareerPathDisplay';
import { API_URL } from "../api/config";

function HomePage() {
  const [activeTab, setActiveTab] = useState('jobSuggestions');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // State for V1
  const [v1Skills, setV1Skills] = useState('');
  const [v1JobTitle, setV1JobTitle] = useState('');
  const [v1Result, setV1Result] = useState(null);

  // State for V2
  const [resumeFile, setResumeFile] = useState(null);
  const [v2Result, setV2Result] = useState(null);

  // State for V3
  const [v3Skills, setV3Skills] = useState('');
  const [v3TargetJob, setV3TargetJob] = useState('');
  const [v3Result, setV3Result] = useState(null);

  const clearError = () => setError(null);

  const handleTabSwitch = (tab) => {
    clearError();
    setActiveTab(tab);
  }

  // --- V1 API Handler (Standalone) ---
  const handleV1Submit = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    setV1Result(null);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ skills: v1Skills.split(',').map(s => s.trim()), job_title: v1JobTitle }),
      });
      if (!response.ok) throw new Error('Skill analysis failed.');
      const data = await response.json();
      if (!data.matching_skills?.length && !data.missing_skills?.length) {
        setError("Could not analyze skills for this job. Please try a different job title.");
        setV1Result(null);
      } else {
        setV1Result(data);
      }
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
    setV2Result(null);
    setError(null);
    const formData = new FormData();
    formData.append("resume_file", resumeFile);
    try {
      const response = await fetch(`${API_URL}/api/suggest-jobs`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error('Job suggestion failed.');
      const data = await response.json();
      if (!data.suggestions?.length) {
        setError("Could not suggest any jobs for this resume. Please try another one.");
        setV2Result(null);
      } else {
        setV2Result(data);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // --- V3 API Handler (Standalone) ---
  const handleV3Submit = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    setV3Result(null);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/generate-path`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ current_skills: v3Skills.split(',').map(s => s.trim()), target_job: v3TargetJob }),
      });
      if (!response.ok) throw new Error('Career path generation failed.');
      const data = await response.json();
      if (!data.milestones?.length && !data.next_skills?.length && !data.recommended_actions?.length) {
        setError("Could not generate a career path for this role.");
        setV3Result(null);
      } else {
        setV3Result(data);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // --- V2 -> V3 Workflow ---
  const handleSuggestionAnalysis = async (jobTitle, skillsForAnalysis) => {
    const skillsPayload = Array.isArray(skillsForAnalysis) ? skillsForAnalysis : [];
    if (skillsPayload.length === 0) {
        setError("Could not find skills from the resume to perform the analysis. Please try again or use the manual input tabs.");
        return;
    }

    setIsLoading(true);
    setV3Result(null);
    setError(null);
    setV3TargetJob(jobTitle);

    try {
      const pathResponse = await fetch(`${API_URL}/api/generate-path`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ current_skills: skillsPayload, target_job: jobTitle }),
      });
      if (!pathResponse.ok) throw new Error('Career path generation failed.');
      const pathData = await pathResponse.json();
      
      if (!pathData.milestones?.length && !pathData.next_skills?.length && !pathData.recommended_actions?.length) {
        setError(`Could not generate a career path for "${jobTitle}". The role may be too specific or not recognized.`);
        setV3Result(null);
        setActiveTab('jobSuggestions'); // Stay on the current tab if it fails
      } else {
        setV3Result(pathData);
        setActiveTab('careerPath'); // Switch to the career path tab on success
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Tabs activeTab={activeTab} setActiveTab={handleTabSwitch} />

      {isLoading && <p>Loading...</p>}
      {error && <p className="error-message">{error}</p>}

      {/* V3 Career Path Tab */}
      {activeTab === 'careerPath' && (
        <>
          {/* Standalone V3 Form */}
          <form className="form-container" onSubmit={handleV3Submit}>
            <div className="input-group">
              <label htmlFor="v3-skills">Your Current Skills (comma-separated)</label>
              <input type="text" id="v3-skills" value={v3Skills} onChange={(e) => setV3Skills(e.target.value)} placeholder="e.g., Python, Git" />
            </div>
            <div className="input-group">
              <label htmlFor="v3-job">Your Target Job</label>
              <input type="text" id="v3-job" value={v3TargetJob} onChange={(e) => setV3TargetJob(e.target.value)} placeholder="e.g., Cloud Engineer" />
            </div>
            <button type="submit" className="analyze-button" disabled={isLoading}>
              {isLoading ? "Generating..." : "Generate Career Path"}
            </button>
          </form>
          {v3Result && <CareerPathDisplay pathData={v3Result} targetJob={v3TargetJob} />}
        </>
      )}

      {/* V2 Job Suggestions Tab */}
      {activeTab === 'jobSuggestions' && (
        <>
          <div className="form-container">
            <div className="input-group">
              <label htmlFor="resume">Upload Your Resume (PDF or DOCX)</label>
              <input type="file" id="resume" accept=".pdf,.docx" onChange={(e) => setResumeFile(e.target.files[0])} />
            </div>
            <button className="analyze-button" onClick={handleV2Submit} disabled={isLoading}>
              {isLoading ? "Analyzing..." : "Suggest Jobs"}
            </button>
          </div>
          {v2Result && <JobSuggestions v2Result={v2Result} onAnalysis={handleSuggestionAnalysis} />}
        </>
      )}

      {/* V1 Skill Gap Analysis Tab */}
      {activeTab === 'gapAnalysis' && (
        <>
          <SkillForm
            skills={v1Skills}
            setSkills={setV1Skills}
            jobTitle={v1JobTitle}
            setJobTitle={setV1JobTitle}
            onSubmit={handleV1Submit}
          />
          {v1Result && <SkillGapResults result={v1Result} />}
        </>
      )}
    </>
  );
}

export default HomePage;