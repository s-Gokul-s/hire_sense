import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
// We assume Chart.js is available or installed.
import Chart from 'chart.js/auto';

const API_BASE_URL = "http://127.0.0.1:8000";

// This component fetches and displays analytical charts using data from the /analytics endpoint.
const AnalyticsPage = () => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Refs for Chart canvases to attach Chart.js instances
  const scoreChartRef = useRef(null);
  const skillsChartRef = useRef(null);
  const gapChartRef = useRef(null);

  // State to hold Chart instances for proper cleanup
  const chartInstances = useRef({});

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Exponential backoff retry logic for stable API calls
      const MAX_RETRIES = 5;
      let attempt = 0;
      let response = null;

      while (attempt < MAX_RETRIES) {
        try {
          response = await fetch(`${API_BASE_URL}/analytics`);
          if (response.ok) break;
        } catch (e) {
          console.warn(`Fetch attempt ${attempt + 1} failed.`);
        }

        attempt++;
        if (attempt < MAX_RETRIES) {
          const delay = Math.pow(2, attempt) * 1000; // 2s, 4s, 8s, ...
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }

      if (!response || !response.ok) {
        const errorData = response ? await response.json() : {};
        throw new Error(errorData.detail || "Failed to fetch analytics data after multiple retries.");
      }
      
      const data = await response.json();
      setAnalyticsData(data);
    } catch (err) {
      setError(err.message);
      setAnalyticsData(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Effect to handle chart rendering and cleanup
  useEffect(() => {
    // Cleanup function to destroy old charts
    const destroyCharts = () => {
        Object.values(chartInstances.current).forEach(chart => {
            if (chart) chart.destroy();
        });
        chartInstances.current = {};
    };

    if (analyticsData) {
      destroyCharts(); // Destroy previous charts before creating new ones

      // 1. Fit Score Distribution (Bar Chart)
      if (scoreChartRef.current) {
        const labels = analyticsData.score_distribution.map(d => d.range);
        const data = analyticsData.score_distribution.map(d => d.count);
        
        chartInstances.current.scoreChart = new Chart(scoreChartRef.current, {
          type: 'bar',
          data: {
            labels: labels,
            datasets: [{
              label: 'Candidate Count',
              data: data,
              backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#6366f1'], // Tailwind colors
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: { beginAtZero: true, title: { display: true, text: 'Number of Candidates' } }
            },
            plugins: { 
              title: { display: true, text: 'Fit Score Distribution' },
              legend: { display: false }
            }
          }
        });
      }

      // 2. Top Skills Summary (Horizontal Bar Chart)
      if (skillsChartRef.current) {
        const sortedSkills = analyticsData.top_skills.slice(0, 8); 
        const labels = sortedSkills.map(d => d.skill);
        const data = sortedSkills.map(d => d.count);

        chartInstances.current.skillsChart = new Chart(skillsChartRef.current, {
          type: 'bar',
          data: {
            labels: labels,
            datasets: [{
              label: 'Frequency Across Resumes',
              data: data,
              backgroundColor: '#8b5cf6', // Violet
              borderWidth: 1
            }]
          },
          options: {
            indexAxis: 'y', // Horizontal bars
            responsive: true,
            maintainAspectRatio: false,
            plugins: { title: { display: true, text: 'Top Skills in Candidate Pool' } }
          }
        });
      }
      
      // 3. Overall Skill Gap (Doughnut Chart)
      if (gapChartRef.current) {
        const gapLabels = ['Total Matched Skills', 'Total Missing Skills'];
        const gapData = [analyticsData.overall_skill_gap.matched, analyticsData.overall_skill_gap.missing];

        chartInstances.current.gapChart = new Chart(gapChartRef.current, {
          type: 'doughnut',
          data: {
            labels: gapLabels,
            datasets: [{
              label: 'Skill Gap Analysis',
              data: gapData,
              backgroundColor: [
                '#10b981', // Matched (Emerald Green)
                '#ef4444' // Missing (Red)
              ],
              hoverOffset: 4
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { 
              title: { display: true, text: 'Overall Matched vs. Missing Skills' },
              legend: { position: 'bottom' }
            }
          }
        });
      }

    }

    // Return the cleanup function
    return destroyCharts;
  }, [analyticsData]);


  if (isLoading) {
    return <div className="text-center p-12 text-2xl text-indigo-600 font-semibold">Loading Analytics...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <header className="bg-white shadow-md p-4 flex justify-between items-center sticky top-0 z-10">
        {/* UPDATED: Change link text to reflect return to results */}
        <Link to="/shortlister" className="text-xl font-bold text-indigo-700 hover:text-indigo-600 transition">
          ← Back to Ranked Resumes
        </Link>
        <div className="flex items-center space-x-2">
          <img
            alt="Logo"
            src="https://tailwindcss.com/plus-assets/img/logos/mark.svg?color=indigo&shade=600"
            className="h-8 w-auto"
          />
          <h1 className="text-2xl font-semibold text-gray-800">Analytics Dashboard</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-4 sm:p-8 mt-8">
        {error ? (
          <div className="text-center p-12 bg-red-50 border-2 border-red-300 text-red-700 rounded-xl shadow-md">
            <p className="text-xl font-bold mb-2">Error Retrieving Data</p>
            <p className="text-lg mb-4">{error}</p>
            <p className="text-sm">Please ensure you have run the **Match Resumes** step successfully before viewing the dashboard.</p>
            <button 
                onClick={fetchData} 
                className="mt-4 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-full transition transform hover:scale-[1.02]"
            >
                Retry Fetch
            </button>
          </div>
        ) : !analyticsData ? (
          <div className="text-center p-12 bg-gray-50 border-2 border-gray-300 rounded-xl shadow-md text-gray-700 font-semibold">
              <p className="text-xl">No analytics data available.</p>
              <p className="text-sm mt-2">Please run the matching process first to generate dashboard data.</p>
          </div>
        ) : (
          <div className="space-y-8 bg-white rounded-xl shadow-2xl p-6 lg:p-10">
            <h2 className="text-4xl font-extrabold text-gray-800 text-center border-b pb-4">
              Candidate Insights Overview 📊
            </h2>
            
            <div className="bg-indigo-50 p-4 rounded-xl shadow-inner text-center font-bold text-indigo-700 text-lg">
              Total Candidates Analyzed: {analyticsData.total_candidates}
            </div>

            {/* Grid for Score Distribution and Skill Gap */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              
              {/* Score Distribution Chart */}
              <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-lg border border-gray-100 h-96">
                <canvas ref={scoreChartRef} className="w-full h-full"></canvas>
              </div>

              {/* Skill Gap Analysis Chart (Doughnut) */}
              <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-100 h-96 flex items-center justify-center">
                <div className="w-full max-w-sm h-full">
                  <canvas ref={gapChartRef}></canvas>
                </div>
              </div>
            </div>
            
            {/* Top Skills Summary Chart (Full Width) */}
            <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-100 h-[450px]">
              <canvas ref={skillsChartRef} className="w-full h-full"></canvas>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default AnalyticsPage;
