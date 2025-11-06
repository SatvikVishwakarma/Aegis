'use client';

import React, { useState, useEffect } from 'react';
import { Download, Server, Users, Package, CheckCircle, AlertCircle, Info } from 'lucide-react';

interface TemplateInfo {
  status: string;
  platform: string;
  runtime: string;
  collectors: string[];
  template_size_mb: number;
  deployment_method: string;
  requirements: string[];
}

export default function AgentsPage() {
  const [serverUrl, setServerUrl] = useState('');
  const [group, setGroup] = useState('');
  const [customGroup, setCustomGroup] = useState('');
  const [isCustomGroup, setIsCustomGroup] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [templateInfo, setTemplateInfo] = useState<TemplateInfo | null>(null);
  const [existingGroups, setExistingGroups] = useState<string[]>([]);

  // Auto-detect server URL from environment
  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
    setServerUrl(apiUrl);
  }, []);

  // Fetch template info on mount
  useEffect(() => {
    fetchTemplateInfo();
    fetchExistingGroups();
  }, []);

  const fetchTemplateInfo = async () => {
    try {
      const token = localStorage.getItem('aegis_token');
      if (!token) return;

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/agents/template-info`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setTemplateInfo(data);
      }
    } catch (err) {
      console.error('Failed to fetch template info:', err);
    }
  };

  const fetchExistingGroups = async () => {
    try {
      const token = localStorage.getItem('aegis_token');
      if (!token) return;

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/nodes`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        // Extract unique groups from nodes
        const groups = [...new Set(data.map((node: any) => node.group).filter(Boolean))];
        setExistingGroups(groups as string[]);
      }
    } catch (err) {
      console.error('Failed to fetch existing groups:', err);
    }
  };

  const handleDownload = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setIsDownloading(true);

    try {
      const token = localStorage.getItem('aegis_token');
      if (!token) {
        throw new Error('Not authenticated. Please login again.');
      }

      // Determine which group to use
      const selectedGroup = isCustomGroup ? customGroup : group;

      if (!selectedGroup) {
        throw new Error('Please select or enter a group name');
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/agents/build-package`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          server_url: serverUrl,
          group: selectedGroup,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to build agent package');
      }

      // Get filename from headers or generate default
      const contentDisposition = response.headers.get('Content-Disposition');
      const filenameMatch = contentDisposition?.match(/filename="(.+)"/);
      const filename = filenameMatch ? filenameMatch[1] : `AegisAgent-${selectedGroup}.zip`;

      // Download file
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setSuccess(`Package downloaded successfully! File: ${filename}`);

    } catch (err: any) {
      setError(err.message || 'Failed to download agent package');
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-3 mb-2">
          <Package className="w-8 h-8 text-blue-500" />
          Download Agent Package
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Build and download a customized Windows agent for endpoint deployment
        </p>
      </div>

      {/* Template Information Card */}
      {templateInfo && (
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6">
          <div className="flex items-start gap-3">
            <Info className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
                Agent Template Information
              </h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600 dark:text-gray-400">Platform:</span>
                  <span className="ml-2 font-medium text-gray-900 dark:text-gray-100">
                    {templateInfo.platform}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600 dark:text-gray-400">Runtime:</span>
                  <span className="ml-2 font-medium text-gray-900 dark:text-gray-100">
                    {templateInfo.runtime}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600 dark:text-gray-400">Package Size:</span>
                  <span className="ml-2 font-medium text-gray-900 dark:text-gray-100">
                    ~{templateInfo.template_size_mb} MB
                  </span>
                </div>
                <div>
                  <span className="text-gray-600 dark:text-gray-400">Deployment:</span>
                  <span className="ml-2 font-medium text-gray-900 dark:text-gray-100">
                    {templateInfo.deployment_method}
                  </span>
                </div>
              </div>
              <div className="mt-3">
                <span className="text-gray-600 dark:text-gray-400 text-sm">Collectors:</span>
                <div className="flex flex-wrap gap-2 mt-1">
                  {templateInfo.collectors.map((collector) => (
                    <span
                      key={collector}
                      className="px-2 py-1 bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-200 rounded text-xs font-medium"
                    >
                      {collector}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Build Form */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <form onSubmit={handleDownload} className="space-y-6">
          {/* Server URL */}
          <div>
            <label className="block text-sm font-medium mb-2">
              <Server className="w-4 h-4 inline mr-2" />
              Server URL
            </label>
            <input
              type="url"
              value={serverUrl}
              onChange={(e) => setServerUrl(e.target.value)}
              placeholder="http://192.168.1.100:5000"
              required
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                       bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100
                       focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Full URL to your Aegis server (agents will connect to this URL)
            </p>
          </div>

          {/* Group Selection */}
          <div>
            <label className="block text-sm font-medium mb-2">
              <Users className="w-4 h-4 inline mr-2" />
              Node Group
            </label>

            <div className="space-y-3">
              {/* Existing Groups */}
              {existingGroups.length > 0 && (
                <div>
                  <label className="flex items-center space-x-2 mb-2">
                    <input
                      type="radio"
                      checked={!isCustomGroup}
                      onChange={() => setIsCustomGroup(false)}
                      className="form-radio text-blue-600"
                    />
                    <span className="text-sm">Select existing group</span>
                  </label>
                  <select
                    value={group}
                    onChange={(e) => setGroup(e.target.value)}
                    disabled={isCustomGroup}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                             bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100
                             focus:ring-2 focus:ring-blue-500 focus:border-transparent
                             disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <option value="">-- Select a group --</option>
                    {existingGroups.map((g) => (
                      <option key={g} value={g}>
                        {g}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Custom Group */}
              <div>
                <label className="flex items-center space-x-2 mb-2">
                  <input
                    type="radio"
                    checked={isCustomGroup}
                    onChange={() => setIsCustomGroup(true)}
                    className="form-radio text-blue-600"
                  />
                  <span className="text-sm">Create new group</span>
                </label>
                <input
                  type="text"
                  value={customGroup}
                  onChange={(e) => setCustomGroup(e.target.value)}
                  placeholder="e.g., production, development, workstations"
                  disabled={!isCustomGroup}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                           bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100
                           focus:ring-2 focus:ring-blue-500 focus:border-transparent
                           disabled:opacity-50 disabled:cursor-not-allowed"
                />
              </div>
            </div>

            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Group name for organizing and filtering endpoints in the dashboard
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="flex items-start gap-3 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
              </div>
            </div>
          )}

          {/* Success Message */}
          {success && (
            <div className="flex items-start gap-3 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
              <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm text-green-800 dark:text-green-200">{success}</p>
              </div>
            </div>
          )}

          {/* Download Button */}
          <button
            type="submit"
            disabled={isDownloading}
            className="w-full flex items-center justify-center gap-2 px-6 py-3 
                     bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg
                     disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isDownloading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Building Package...
              </>
            ) : (
              <>
                <Download className="w-5 h-5" />
                Download Agent Package
              </>
            )}
          </button>
        </form>
      </div>

      {/* Deployment Instructions */}
      <div className="mt-8 bg-gray-50 dark:bg-gray-800/50 rounded-lg p-6">
        <h3 className="font-semibold text-lg mb-4">📦 Deployment Instructions</h3>
        <ol className="space-y-3 text-sm text-gray-700 dark:text-gray-300">
          <li className="flex gap-3">
            <span className="font-bold text-blue-600 dark:text-blue-400">1.</span>
            <span>
              <strong>Download</strong> the agent package ZIP file to your local machine
            </span>
          </li>
          <li className="flex gap-3">
            <span className="font-bold text-blue-600 dark:text-blue-400">2.</span>
            <span>
              <strong>Extract</strong> the ZIP file to a permanent location on the target endpoint 
              (e.g., <code className="bg-gray-200 dark:bg-gray-700 px-1 rounded">C:\AegisAgent\</code>)
            </span>
          </li>
          <li className="flex gap-3">
            <span className="font-bold text-blue-600 dark:text-blue-400">3.</span>
            <span>
              <strong>Run PowerShell</strong> as Administrator on the target endpoint
            </span>
          </li>
          <li className="flex gap-3">
            <span className="font-bold text-blue-600 dark:text-blue-400">4.</span>
            <span>
              <strong>Navigate</strong> to the extracted folder and run:{' '}
              <code className="bg-gray-200 dark:bg-gray-700 px-1 rounded">.\INSTALL.ps1</code>
            </span>
          </li>
          <li className="flex gap-3">
            <span className="font-bold text-blue-600 dark:text-blue-400">5.</span>
            <span>
              <strong>Choose</strong> installation type (Windows Service recommended for production)
            </span>
          </li>
          <li className="flex gap-3">
            <span className="font-bold text-blue-600 dark:text-blue-400">6.</span>
            <span>
              <strong>Verify</strong> the endpoint appears in the <strong>Nodes</strong> page within 30 seconds
            </span>
          </li>
        </ol>

        <div className="mt-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded">
          <p className="text-sm text-yellow-800 dark:text-yellow-200">
            <strong>⚠️ Important:</strong> Administrator privileges are required for Windows Service installation.
            Ensure the target endpoint has network access to the server URL specified above.
          </p>
        </div>
      </div>
    </div>
  );
}
