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

  const handleGetResults = () => {
    // 🔁 Replace with actual ML model integration later
    const mockResults = resumes.map((file, index) => ({
      name: file.name,
      score: Math.random() * 100,
    })).sort((a, b) => b.score - a.score)

    setRankedResumes(mockResults)
    setShowResults(true)
  }

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

        <div className="mt-6 flex justify-center">
          <button
            onClick={handleGetResults}
            disabled={!jobDescription || resumes.length === 0}
            className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-6 py-3 rounded-md shadow-md disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            Get Result
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
