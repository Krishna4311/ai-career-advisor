import { useState } from 'react';
import './App.css';
import SkillForm from './components/SkillForm';

function App() {
  const [skills, setSkills] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  
  // State for the results, loading status, and errors
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // --- IMPORTANT: PASTE YOUR BACKEND URL HERE ---
  const API_URL = ""; // Get this from your Cloud Shell Web Preview

  const handleSubmit = async () => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    // The skills need to be sent as an array
    const skillsArray = skills.split(',').map(skill => skill.trim());

    try {
      const response = await fetch(`${API_URL}/api/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          skills: skillsArray,
          job_title: jobTitle,
        }),
      });

      if (!response.ok) {
        throw new Error('Something went wrong. Please try again.');
      }

      const data = await response.json();
      setResult(data);

    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <h1>AI Career Advisor</h1>
      <SkillForm
        skills={skills}
        setSkills={setSkills}
        jobTitle={jobTitle}
        setJobTitle={setJobTitle}
        handleSubmit={handleSubmit}
      />
      
      {/* We will add the results display here in the next step */}
      {isLoading && <p>Analyzing your skills...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {result && (
        <div style={{ textAlign: 'left', marginTop: '2rem' }}>
          <h2>Analysis Complete</h2>
          <h3>Matching Skills:</h3>
          <ul>
            {result.matching_skills.map((skill, index) => <li key={index}>{skill}</li>)}
          </ul>
          <h3>Missing Skills:</h3>
          <ul>
            {result.missing_skills.map((skill, index) => <li key={index}>{skill}</li>)}
          </ul>
        </div>
      )}
    </>
  );
}

export default App;