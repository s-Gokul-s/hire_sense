import React, { useState } from 'react';

export default function RankedResumeList({ rankedResumes, setRankedResumes, numToShow }) {
  const [selectedResume, setSelectedResume] = useState(null);
  const [insights, setInsights] = useState(null);

  const handleAccept = async (resumeToAccept) => {
    try {
      // NOTE: Acceptance moves the file to 'accepted_resumes' on the backend.
      await fetch(`http://127.0.0.1:8000/accept-resume/${resumeToAccept.filename}`, {
        method: 'POST',
      });
      // Remove from the current ranked list in the UI
      setRankedResumes(rankedResumes.filter(r => r.filename !== resumeToAccept.filename));
      if (selectedResume && selectedResume.filename === resumeToAccept.filename) {
          setSelectedResume(null); // Close the modal if it's open
      }
    } catch (error) {
      console.error('Failed to accept resume:', error);
    }
  };

  const handleReject = async (resumeToReject) => {
    try {
      // 1. Call the new backend DELETE endpoint to remove the file from temp_resumes
      const response = await fetch(`http://127.0.0.1:8000/reject-resume/${resumeToReject.filename}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
          throw new Error(`Backend deletion failed: ${response.statusText}`);
      }
      
      // 2. Remove from the current ranked list in the UI (local state cleanup)
      setRankedResumes(rankedResumes.filter(r => r.filename !== resumeToReject.filename));
      
      // 3. Close the modal if the rejected resume was being viewed
      if (selectedResume && selectedResume.filename === resumeToReject.filename) {
          setSelectedResume(null); 
      }
      
    } catch (error) {
        console.error('Failed to reject resume and delete file:', error);
        // Optional: Provide visual feedback to the user about the error
    }
  };

  const getBarColor = (score) => {
    if (score >= 90) return 'bg-green-500';
    if (score >= 70) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const handleView = async (resume) => {
    setSelectedResume(resume);

    try {
      const response = await fetch(`http://127.0.0.1:8000/insights/${resume.filename}`);
      if (!response.ok) {
        throw new Error('Failed to fetch insights');
      }
      const data = await response.json();
      setInsights(data);
    } catch (error) {
      console.error('Error fetching insights:', error);
      setInsights(null);
    }
  };

  // NEW: Pass the `numToShow` value as a query parameter
  const handleDownloadExcel = () => {
    window.location.href = `http://127.0.0.1:8000/reports/export-excel?limit=${numToShow}`;
  };
  
  const handleDownloadZip = () => {
    window.location.href = `http://127.0.0.1:8000/reports/download-resumes-zip?limit=${numToShow}`;
  };


  if (!rankedResumes || rankedResumes.length === 0) {
    return null;
  }

  return (
    <div className="mt-10 p-6 bg-white shadow-lg rounded-lg border border-gray-200">
      <div className="flex justify-between items-center mb-4 flex-wrap gap-3">
        <h2 className="text-xl font-semibold text-gray-800">Ranked Resumes</h2>
        
        {/* Updated Download Buttons: Removed CSV button */}
        <div className="flex space-x-2">
            <button
                onClick={handleDownloadExcel}
                className="bg-green-600 hover:bg-green-500 text-white font-semibold py-2 px-4 rounded-md transition duration-200 shadow-md text-sm"
            >
                Export Excel 📊
            </button>
            <button
                onClick={handleDownloadZip}
                className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 px-4 rounded-md transition duration-200 shadow-md text-sm"
            >
                Download ZIP 📁
            </button>
        </div>
      </div>

      <ol className="list-decimal list-inside space-y-3">
        {rankedResumes.map((resume, index) => (
          <li
            key={index}
            className="p-3 bg-gray-50 rounded-md shadow-sm transition"
          >
            <p className="text-lg font-medium text-gray-700">
              {index + 1}. {resume.filename}
            </p>
            
            <div className="mt-2">
              <div className="flex justify-between mb-1 text-sm font-medium text-gray-700">
                <span>Fit Score: {resume.score}%</span>
                <span>{resume.prediction}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div 
                  className={`h-2.5 rounded-full ${getBarColor(resume.score)}`} 
                  style={{ width: `${resume.score}%` }}
                ></div>
              </div>
            </div>

            <div className="mt-4 space-x-2">
              <button
                className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-1 px-3 rounded-md transition"
                onClick={() => handleView(resume)}
              >
                View
              </button>
              <button
                className="bg-green-600 hover:bg-green-500 text-white font-semibold py-1 px-3 rounded-md transition"
                onClick={() => handleAccept(resume)}
              >
                Accept
              </button>
              <button
                className="bg-red-600 hover:bg-red-500 text-white font-semibold py-1 px-3 rounded-md transition"
                onClick={() => handleReject(resume)}
              >
                Reject
              </button>
            </div>
          </li>
        ))}
      </ol>

      {selectedResume && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex justify-center items-center z-50">
          <div className="bg-white p-8 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <h3 className="text-2xl font-bold mb-4">{selectedResume.filename}</h3>
            
            {insights && (
              <div className="mb-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
                <p className="text-sm font-semibold text-gray-700">Skill Breakdown:</p>
                {insights.matched_skills.length > 0 && (
                    <p className="text-sm text-green-700 mt-1">
                        <span className="font-bold">Matched Skills:</span> {insights.matched_skills.join(', ')}
                    </p>
                )}
                {insights.missing_skills.length > 0 && (
                    <p className="text-sm text-red-700 mt-1">
                        <span className="font-bold">Missing Skills:</span> {insights.missing_skills.join(', ')}
                    </p>
                )}
              </div>
            )}
            
            <iframe
              src={`http://127.0.0.1:8000/resumes/${selectedResume.filename}`}
              width="100%"
              height="600px"
              className="border border-gray-300 rounded-md"
            ></iframe>
            <button
              className="mt-4 bg-gray-600 hover:bg-gray-500 text-white font-semibold py-2 px-4 rounded-md"
              onClick={() => { setSelectedResume(null); setInsights(null); }}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}