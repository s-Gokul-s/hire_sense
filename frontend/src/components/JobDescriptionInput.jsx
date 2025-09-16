import React, { useState } from 'react';

export default function JobDescriptionInput({ jobDescription, setJobDescription }) {
  const [inputMode, setInputMode] = useState('text'); // 'text' or 'file'

  const handleFileChange = (e) => {
    setJobDescription(e.target.files[0]);
  };

  const handleTextChange = (e) => {
    setJobDescription(e.target.value);
  };

  return (
    <div className="mb-6">
      <div className="flex justify-between items-center mb-2">
        <label className="block text-lg font-medium text-gray-700">
          Job Description
        </label>
        <button
          onClick={() => setInputMode(inputMode === 'text' ? 'file' : 'text')}
          className="text-indigo-600 hover:text-indigo-500 text-sm font-semibold transition"
        >
          {inputMode === 'text' ? 'Switch to File Upload' : 'Switch to Text Input'}
        </button>
      </div>

      {inputMode === 'text' ? (
        <textarea
          id="jobDescription"
          name="jobDescription"
          rows={8}
          className="w-full p-4 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
          placeholder="Paste or write the job description here..."
          value={jobDescription}
          onChange={handleTextChange}
        />
      ) : (
        <input
          id="jobDescriptionFile"
          type="file"
          accept=".pdf,.doc,.docx"
          onChange={handleFileChange}
          className="block w-full text-sm text-gray-600 file:mr-4 file:py-2 file:px-4
                     file:rounded-md file:border-0
                     file:text-sm file:font-semibold
                     file:bg-indigo-50 file:text-indigo-700
                     hover:file:bg-indigo-100"
        />
      )}
    </div>
  );
}