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
            <p className="text-lg font-medium text-gray-700">{resume.filename}</p>
            {/* 💡 Fixed: Changed `resume.name` to `resume.filename` */}
            {resume.score && typeof resume.score === 'number' && (
              <p className="text-sm text-gray-500">
                Fit Score: {resume.score.toFixed(2)} -
                <span className={`font-bold ml-1 ${resume.prediction === 'Fit' ? 'text-green-600' : 'text-red-600'}`}>
                  {resume.prediction}
                </span>
              </p>
            )}
            {!resume.score || typeof resume.score !== 'number' && (
              <p className="text-sm text-gray-500">Fit Score: N/A</p>
            )}
          </li>
        ))}
      </ol>
    </div>
  );
}