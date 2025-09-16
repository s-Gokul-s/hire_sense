import React from 'react';

export default function ResumeUpload({ resumes, setResumes }) {
  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setResumes(selectedFiles);
  };

  const fileCount = resumes.length;
  const maxDisplay = 5;

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
      {fileCount > 0 && (
        <div className="mt-4 p-4 border border-gray-200 rounded-md bg-gray-50">
          <p className="text-sm font-semibold text-gray-700">
            {fileCount} {fileCount === 1 ? 'file' : 'files'} selected:
          </p>
          <ul className="mt-2 list-disc list-inside text-sm text-gray-700">
            {resumes.slice(0, maxDisplay).map((file, idx) => (
              <li key={idx}>{file.name}</li>
            ))}
          </ul>
          {fileCount > maxDisplay && (
            <p className="mt-2 text-sm text-gray-500 italic">
              And {fileCount - maxDisplay} more...
            </p>
          )}
        </div>
      )}
    </div>
  );
}