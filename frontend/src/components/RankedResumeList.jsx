import React from 'react';

export default function RankedResumeList({ rankedResumes }) {
  if (!rankedResumes || rankedResumes.length === 0) {
    return null; // Don't render anything if no results
  }

  return (
    <div className="mt-10 p-6 bg-white shadow-lg rounded-lg border border-gray-200">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Ranked Resumes</h2>
      <ol className="list-decimal list-inside space-y-3">
        {rankedResumes.map((resume, index) => (
          <li key={index} className="p-3 bg-gray-50 rounded-md shadow-sm">
            <p className="text-lg font-medium text-gray-700">{resume.name}</p>
            {resume.score && (
              <p className="text-sm text-gray-500">Fit Score: {resume.score.toFixed(2)}</p>
            )}
          </li>
        ))}
      </ol>
    </div>
  );
}
