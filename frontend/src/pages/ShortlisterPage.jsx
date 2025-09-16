'use client'

import { useState } from 'react'
import JobDescriptionInput from '../components/JobDescriptionInput.jsx'
import ResumeUpload from '../components/ResumeUpload.jsx'
import RankedResumeList from '../components/RankedResumeList.jsx'

export default function ShortlisterPage() {
  const [jobDescription, setJobDescription] = useState('')
  const [resumes, setResumes] = useState([])
  const [rankedResumes, setRankedResumes] = useState([])
  const [showResults, setShowResults] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const handleGetResults = async () => {
    setIsLoading(true);
    setShowResults(false);

    try {
      // Step 1: Upload Job Description
      const jdFormData = new FormData();
      if (jobDescription instanceof File) {
        jdFormData.append('jd_upload', jobDescription);
      } else {
        jdFormData.append('jd_text', jobDescription); 
      }
      await fetch('http://127.0.0.1:8000/upload-jd', {
        method: 'POST',
        body: jdFormData,
      });

      // Step 2: Upload Resumes
      const resumeFormData = new FormData();
      resumes.forEach(file => {
        resumeFormData.append('files', file); 
      });
      await fetch('http://127.0.0.1:8000/upload-resumes', {
        method: 'POST',
        body: resumeFormData,
      });

      // Step 3: Get Ranked Results from the Matching Engine
      const response = await fetch('http://127.0.0.1:8000/match', {
        method: 'POST',
      });
      const data = await response.json();
      setRankedResumes(data.ranked_resumes);
      setShowResults(true);

    } catch (error) {
      console.error('An error occurred during the shortlisting process:', error);
    } finally {
      setIsLoading(false);
    }
  }

  const handleReset = async () => {
    try {
      await fetch('http://127.0.0.1:8000/reset/', {
        method: 'POST',
      });
      setJobDescription('');
      setResumes([]);
      setRankedResumes([]);
      setShowResults(false);
      console.log('Session has been reset successfully.');
    } catch (error) {
      console.error('Failed to reset the session:', error);
    }
  };

  return (
    <div className="min-h-screen bg-white font-[Montserrat]">
      {/* Header */}
      <header className="w-full px-6 py-4 shadow-md bg-white flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <img
            src="https://tailwindcss.com/plus-assets/img/logos/mark.svg?color=indigo&shade=600"
            alt="Logo"
            className="h-8 w-8"
          />
          <h1 className="text-xl font-semibold text-indigo-700">HireSense Shortlister</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto p-6 mt-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center">
          Upload Job Description & Resumes
        </h2>

        <JobDescriptionInput
          jobDescription={jobDescription}
          setJobDescription={setJobDescription}
        />

        <ResumeUpload resumes={resumes} setResumes={setResumes} />

        <div className="mt-6 flex justify-center space-x-4">
          <button
            onClick={handleGetResults}
            disabled={(!jobDescription && resumes.length === 0) || isLoading}
            className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-6 py-3 rounded-md shadow-md disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {isLoading ? 'Processing...' : 'Get Result'}
          </button>
          <button
            onClick={handleReset}
            className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold px-6 py-3 rounded-md shadow-md transition"
          >
            Reset
          </button>
        </div>

        {showResults && (
          <div className="mt-10">
            <RankedResumeList rankedResumes={rankedResumes} />
          </div>
        )}
      </main>
    </div>
  )
}