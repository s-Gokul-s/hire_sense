import React from 'react';

export default function ResumeUpload({ resumes, setResumes }) {
  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setResumes(selectedFiles);
  };

  return (
    <div className="mb-6">
      <label htmlFor="resumeUpload" className="block text-lg font-medium text-gray-700 mb-2">
        Upload Resumes
      </label>
      <input
        id="resumeUpload"
        type="file"
        accept=".pdf,.doc,.docx"
        multiple
        onChange={handleFileChange}
        className="block w-full text-sm text-gray-600 file:mr-4 file:py-2 file:px-4
                   file:rounded-md file:border-0
                   file:text-sm file:font-semibold
                   file:bg-indigo-50 file:text-indigo-700
                   hover:file:bg-indigo-100"
      />
      {resumes.length > 0 && (
        <ul className="mt-4 list-disc list-inside text-sm text-gray-700">
          {resumes.map((file, idx) => (
            <li key={idx}>{file.name}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
