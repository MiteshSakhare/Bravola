import { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { fetchMerchantProfile } from '@/store/slices/merchantSlice';
import { merchantApi } from '@/api/merchants'; // Adjust import path if needed

const Settings = () => {
  const dispatch = useDispatch();
  const { profile } = useSelector((state) => state.merchant);
  
  // Local state for form
  const [formData, setFormData] = useState({
    shop_name: '',
    monthly_revenue: 0,
    shopify_access_token: '',
    klaviyo_api_key: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);

  // Load profile data into form on mount
  useEffect(() => {
    if (profile) {
      setFormData({
        shop_name: profile.shop_name || '',
        monthly_revenue: profile.monthly_revenue || 0,
        shopify_access_token: profile.shopify_access_token || '',
        klaviyo_api_key: profile.klaviyo_api_key || ''
      });
    } else {
      dispatch(fetchMerchantProfile());
    }
  }, [profile, dispatch]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatus(null);
    try {
      // ✅ FIX: Update profile data (Name/Revenue)
      await merchantApi.updateProfile({
        shop_name: formData.shop_name,
        monthly_revenue: Number(formData.monthly_revenue)
      });
      
      // ✅ FIX: Update Integrations
      await merchantApi.updateIntegrations({
        shopify_access_token: formData.shopify_access_token,
        klaviyo_api_key: formData.klaviyo_api_key
      });

      // Refresh global state
      dispatch(fetchMerchantProfile());
      setStatus({ type: 'success', msg: '✅ Settings saved successfully!' });
    } catch (err) {
      console.error(err);
      setStatus({ type: 'error', msg: '❌ Failed to save. Try again.' });
    }
    setLoading(false);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-slide-in">
      <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
      
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <h2 className="text-xl font-semibold mb-4">Store Profile</h2>
        <div className="grid gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Shop Name</label>
            <input 
              type="text" 
              value={formData.shop_name}
              onChange={(e) => setFormData({...formData, shop_name: e.target.value})}
              className="w-full px-4 py-2 border rounded-lg"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Monthly Revenue ($)</label>
            <input 
              type="number" 
              value={formData.monthly_revenue}
              onChange={(e) => setFormData({...formData, monthly_revenue: e.target.value})}
              className="w-full px-4 py-2 border rounded-lg"
            />
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <h2 className="text-xl font-semibold mb-4">API Integrations</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Shopify Access Token</label>
            <input 
              type="password" 
              value={formData.shopify_access_token}
              onChange={(e) => setFormData({...formData, shopify_access_token: e.target.value})}
              className="w-full px-4 py-2 border rounded-lg bg-gray-50"
              placeholder="shpat_..."
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Klaviyo API Key</label>
            <input 
              type="password" 
              value={formData.klaviyo_api_key}
              onChange={(e) => setFormData({...formData, klaviyo_api_key: e.target.value})}
              className="w-full px-4 py-2 border rounded-lg bg-gray-50"
              placeholder="pk_..."
            />
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <button 
          onClick={handleSubmit}
          disabled={loading}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
        >
          {loading ? 'Saving...' : 'Save Changes'}
        </button>
        {status && (
          <span className={status.type === 'success' ? 'text-green-600' : 'text-red-600'}>
            {status.msg}
          </span>
        )}
      </div>
    </div>
  );
};

export default Settings;