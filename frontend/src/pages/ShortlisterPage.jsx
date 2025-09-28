'use client'

import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import JobDescriptionInput from '../components/JobDescriptionInput.jsx'
import ResumeUpload from '../components/ResumeUpload.jsx'
import RankedResumeList from '../components/RankedResumeList.jsx'
import { PlusCircle, BarChart2, RotateCw } from 'lucide-react'

// Helper function to safely get initial state from session storage
const getInitialState = (key, defaultValue) => {
  if (typeof window !== 'undefined') {
    const stored = sessionStorage.getItem(key);
    if (stored) {
      try {
        return JSON.parse(stored);
      } catch (e) {
        sessionStorage.removeItem(key);
        console.error(`Error parsing sessionStorage key '${key}':`, e);
      }
    }
  }
  return defaultValue;
};

export default function ShortlisterPage() {
  const navigate = useNavigate()

  // 1. Initialize state from sessionStorage
  const [jobDescription, setJobDescription] = useState(() => getInitialState('jobDescription', ''))
  const [resumes, setResumes] = useState([])
  const [rankedResumes, setRankedResumes] = useState(() => getInitialState('rankedResumes', []))
  const [showResults, setShowResults] = useState(() => getInitialState('showResults', false))

  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  
  // NEW state for filtering resumes
  const [numToShow, setNumToShow] = useState(10) // default show top 10
  const [warning, setWarning] = useState("")

  const API_BASE_URL = 'http://127.0.0.1:8000';

  // Persist rankedResumes and showResults
  useEffect(() => {
    sessionStorage.setItem('rankedResumes', JSON.stringify(rankedResumes));
    sessionStorage.setItem('showResults', JSON.stringify(showResults));
  }, [rankedResumes, showResults]);

  // Persist jobDescription
  useEffect(() => {
    if (typeof jobDescription === 'string' && jobDescription.trim() !== '') {
      sessionStorage.setItem('jobDescription', JSON.stringify(jobDescription));
    } else {
      sessionStorage.removeItem('jobDescription');
    }
  }, [jobDescription]);

  const handleGetResults = async () => {
    setIsLoading(true);
    setError(null);
    setShowResults(false);
    setRankedResumes([]);

    try {
      if (!jobDescription || resumes.length === 0) {
        throw new Error("Please provide a Job Description AND upload at least one resume.");
      }

      // Step 1: Upload Job Description
      const jdFormData = new FormData();
      if (jobDescription instanceof File) {
        jdFormData.append('jd_upload', jobDescription);
      } else {
        jdFormData.append('jd_text', jobDescription);
      }
      const jdResponse = await fetch(`${API_BASE_URL}/upload-jd`, {
        method: 'POST',
        body: jdFormData,
      });
      if (!jdResponse.ok) {
        throw new Error(`JD Upload failed: ${jdResponse.statusText}`);
      }

      // Step 2: Upload Resumes
      const resumeFormData = new FormData();
      resumes.forEach(file => {
        resumeFormData.append('files', file);
      });
      const resumeResponse = await fetch(`${API_BASE_URL}/upload-resumes`, {
        method: 'POST',
        body: resumeFormData,
      });
      if (!resumeResponse.ok) {
        throw new Error(`Resume Upload failed: ${resumeResponse.statusText}`);
      }

      // Step 3: Get Ranked Results
      const matchResponse = await fetch(`${API_BASE_URL}/match`, {
        method: 'POST',
      });
      if (!matchResponse.ok) {
        const errorData = await matchResponse.json();
        throw new Error(errorData.detail || `Matching failed with status: ${matchResponse.status}`);
      }

      const data = await matchResponse.json();
      setRankedResumes(data.ranked_resumes);
      setShowResults(true);

      // reset filter to default after new results
      setNumToShow(10);
      setWarning("");

    } catch (err) {
      console.error('An error occurred during the shortlisting process:', err);
      setError(err.message || 'An unexpected error occurred during processing.');
    } finally {
      setIsLoading(false);
    }
  }

  const handleReset = async () => {
    try {
      await fetch(`${API_BASE_URL}/reset/`, {
        method: 'POST',
      });
      setJobDescription('');
      setResumes([]);
      setRankedResumes([]);
      setShowResults(false);
      setError(null);
      setNumToShow(10);
      setWarning("");

      sessionStorage.removeItem('jobDescription');
      sessionStorage.removeItem('rankedResumes');
      sessionStorage.removeItem('showResults');

      console.log('Session has been reset successfully.');
    } catch (error) {
      console.error('Failed to reset the session:', error);
    }
  };

  const handleGoToAnalytics = () => {
    navigate('/analytics', { state: { rankedResumes: rankedResumes } });
  }

  return (
    <div className="min-h-screen bg-gray-50 font-[Montserrat]">
      {/* Header */}
      <header className="w-full px-6 py-4 shadow-md bg-white flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center space-x-2">
          <Link to="/" className="-m-1.5 p-1.5 flex items-center space-x-2">
            <img
              src="https://tailwindcss.com/plus-assets/img/logos/mark.svg?color=indigo&shade=600"
              alt="Logo"
              className="h-8 w-8"
            />
            <h1 className="text-xl font-semibold text-indigo-700">HireSense Shortlister</h1>
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto p-6 mt-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center">
          AI-Powered Resume Matching
        </h2>

        {!showResults ? (
          // --- Input Section ---
          <div className="bg-white p-6 shadow-xl rounded-lg border border-gray-200 mb-10 max-w-4xl mx-auto">
            <JobDescriptionInput jobDescription={jobDescription} setJobDescription={setJobDescription} />
            <ResumeUpload resumes={resumes} setResumes={setResumes} />

            {error && (
              <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md text-sm">
                Error: {error}
              </div>
            )}

            <div className="mt-6 flex justify-center space-x-4">
              <button
                onClick={handleGetResults}
                disabled={(!jobDescription || resumes.length === 0) || isLoading}
                className="flex items-center space-x-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-6 py-3 rounded-xl shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition duration-200 transform hover:scale-[1.01]"
              >
                {isLoading ?
                  (<><RotateCw className="w-5 h-5 animate-spin"/><span>Processing...</span></>) :
                  (<><PlusCircle className="w-5 h-5"/><span>Get Ranked Result</span></>)
                }
              </button>
              <button
                onClick={handleReset}
                className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold px-6 py-3 rounded-xl shadow-md transition duration-200"
              >
                Reset
              </button>
            </div>
          </div>
        ) : (
          // --- Results Section ---
          <>
            <div className="flex flex-col md:flex-row justify-between items-center mb-6 p-4 bg-white shadow-xl rounded-lg border border-indigo-100">
              <h3 className="text-2xl font-bold text-gray-800 mb-4 md:mb-0">
                Top Candidate Matches ({rankedResumes.length} total)
              </h3>

              <div className="flex space-x-3 items-center">
                <input
                  type="number"
                  min="1"
                  className="w-24 px-2 py-1 border border-gray-300 rounded-md"
                  value={numToShow}
                  onChange={(e) => {
                    const val = parseInt(e.target.value) || 0;
                    if (val > rankedResumes.length) {
                      setWarning(`Only ${rankedResumes.length} resumes available.`);
                      setNumToShow(rankedResumes.length);
                    } else {
                      setWarning("");
                      setNumToShow(val);
                    }
                  }}
                />
                <span className="text-gray-600 text-sm">resumes to display</span>

                <button
                  onClick={handleGoToAnalytics}
                  className="flex items-center space-x-2 bg-green-600 hover:bg-green-700 text-white font-semibold px-5 py-2 rounded-xl shadow-lg transition duration-200"
                  title="View Aggregate Data & Charts"
                >
                  <BarChart2 className="w-5 h-5"/>
                  <span>View Analytics</span>
                </button>
                <button
                  onClick={handleReset}
                  className="flex items-center space-x-2 bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold px-5 py-2 rounded-xl shadow-md transition duration-200"
                  title="Start New Shortlisting Session"
                >
                  <RotateCw className="w-5 h-5"/>
                  <span>Start New</span>
                </button>
              </div>
            </div>

            {warning && (
              <div className="mb-4 p-2 bg-yellow-100 border border-yellow-400 text-yellow-700 rounded-md text-sm">
                {warning}
              </div>
            )}

            <RankedResumeList
              rankedResumes={rankedResumes.slice(0, numToShow)}
              setRankedResumes={setRankedResumes}
              numToShow={numToShow}
              totalResumesCount={rankedResumes.length}
              API_BASE_URL={API_BASE_URL}
            />
          </>
        )}
      </main>
    </div>
  )
}