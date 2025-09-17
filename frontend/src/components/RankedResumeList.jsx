import React from 'react';

export default function RankedResumeList({ rankedResumes, setRankedResumes }) {
  const handleAccept = async (filename) => {
    try {
      await fetch(`http://127.0.0.1:8000/accept-resume/${filename}`, {
        method: 'POST',
      });
      setRankedResumes(rankedResumes.filter(r => r.filename !== filename));
    } catch (error) {
      console.error('Failed to accept resume:', error);
    }
  };

  const handleReject = (filename) => {
    setRankedResumes(rankedResumes.filter(r => r.filename !== filename));
  };

  const getBarColor = (score) => {
    if (score >= 90) return 'bg-green-500';
    if (score >= 70) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (!rankedResumes || rankedResumes.length === 0) {
    return null;
  }

  return (
    <div className="mt-10 p-6 bg-white shadow-lg rounded-lg border border-gray-200">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Ranked Resumes</h2>
      <ol className="list-decimal list-inside space-y-3">
        {rankedResumes.map((resume, index) => (
          <li
            key={index}
            className="p-3 bg-gray-50 rounded-md shadow-sm transition"
          >
            <p className="text-lg font-medium text-gray-700">
              {index + 1}. {resume.filename}
            </p>
            
            {/* 💡 NEW: The Confidence Bar */}
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

            {/* Accept/Reject buttons */}
            <div className="mt-4 space-x-2">
              <button
                className="bg-green-600 hover:bg-green-500 text-white font-semibold py-1 px-3 rounded-md transition"
                onClick={() => handleAccept(resume.filename)}
              >
                Accept
              </button>
              <button
                className="bg-red-600 hover:bg-red-500 text-white font-semibold py-1 px-3 rounded-md transition"
                onClick={() => handleReject(resume.filename)}
              >
                Reject
              </button>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}