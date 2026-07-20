import React, { useState } from 'react';
import { Leaf, Droplets, MapPin, Users } from 'lucide-react';

const Onboarding = ({ session, onComplete }) => {
  const [formData, setFormData] = useState({
    name: '',
    location: '',
    water_source: '',
    household_size: 4
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/v1/auth/onboard`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to complete onboarding');
      }

      const data = await response.json();
      onComplete(data.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <Droplets className="mx-auto h-12 w-12 text-blue-500" />
        <h2 className="mt-6 text-3xl font-extrabold text-white">Complete your Profile</h2>
        <p className="mt-2 text-sm text-slate-400">
          Tell us a bit about yourself and your water source.
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-slate-900 py-8 px-4 shadow sm:rounded-lg sm:px-10 border border-slate-800">
          <form className="space-y-6" onSubmit={handleSubmit}>
            {error && (
              <div className="bg-red-500/10 border border-red-500/50 text-red-500 p-3 rounded text-sm">
                {error}
              </div>
            )}
            
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-slate-300">
                Full Name
              </label>
              <div className="mt-1 relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Leaf className="h-5 w-5 text-slate-500" />
                </div>
                <input
                  id="name"
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="appearance-none block w-full pl-10 px-3 py-2 border border-slate-700 rounded-md shadow-sm bg-slate-800 text-white placeholder-slate-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="John Doe"
                />
              </div>
            </div>

            <div>
              <label htmlFor="location" className="block text-sm font-medium text-slate-300">
                Location
              </label>
              <div className="mt-1 relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <MapPin className="h-5 w-5 text-slate-500" />
                </div>
                <input
                  id="location"
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData({...formData, location: e.target.value})}
                  className="appearance-none block w-full pl-10 px-3 py-2 border border-slate-700 rounded-md shadow-sm bg-slate-800 text-white placeholder-slate-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="City, State"
                />
              </div>
            </div>
            
            <div>
              <label htmlFor="water_source" className="block text-sm font-medium text-slate-300">
                Primary Water Source
              </label>
              <div className="mt-1 relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Droplets className="h-5 w-5 text-slate-500" />
                </div>
                <select
                  id="water_source"
                  value={formData.water_source}
                  onChange={(e) => setFormData({...formData, water_source: e.target.value})}
                  className="appearance-none block w-full pl-10 px-3 py-2 border border-slate-700 rounded-md shadow-sm bg-slate-800 text-white focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                >
                  <option value="">Select a source</option>
                  <option value="Municipal Tap">Municipal Tap</option>
                  <option value="Groundwater Well">Groundwater Well</option>
                  <option value="River/Lake">River / Lake</option>
                  <option value="Rainwater Harvesting">Rainwater Harvesting</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>

            <div>
              <label htmlFor="household_size" className="block text-sm font-medium text-slate-300">
                Household Size
              </label>
              <div className="mt-1 relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Users className="h-5 w-5 text-slate-500" />
                </div>
                <input
                  id="household_size"
                  type="number"
                  min="1"
                  value={formData.household_size}
                  onChange={(e) => setFormData({...formData, household_size: parseInt(e.target.value) || 1})}
                  className="appearance-none block w-full pl-10 px-3 py-2 border border-slate-700 rounded-md shadow-sm bg-slate-800 text-white focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {loading ? 'Saving...' : 'Complete Profile'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Onboarding;
