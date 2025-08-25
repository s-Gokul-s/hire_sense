import React from 'react';

export default function JobDescriptionInput({ jobDescription, setJobDescription }) {
  return (
    <div className="mb-6">
      <label htmlFor="jobDescription" className="block text-lg font-medium text-gray-700 mb-2">
        Job Description
      </label>
      <textarea
        id="jobDescription"
        name="jobDescription"
        rows={8}
        className="w-full p-4 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
        placeholder="Paste or write the job description here..."
        value={jobDescription}
        onChange={(e) => setJobDescription(e.target.value)}
      />
    </div>
  );
}
