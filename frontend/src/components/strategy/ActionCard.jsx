import { useState } from 'react';
import { strategyApi } from '../../api/strategy';

const ActionCard = ({ strategy }) => {
  const [deploying, setDeploying] = useState(false);
  const [feedbackStatus, setFeedbackStatus] = useState(null); // 'approved' | 'rejected'

  const handleDeploy = async () => {
    setDeploying(true);
    try {
      // Note: In a full app, you'd show a modal to select the Klaviyo List ID.
      // We are using a placeholder ID here for the MVP pilot.
      await strategyApi.deployStrategy(strategy.strategy_id, 'WXy7zQ'); 
      alert('✅ Strategy successfully deployed to Klaviyo!');
    } catch (err) {
      alert('❌ Deployment failed. Please check your Klaviyo API Key in Settings.');
    }
    setDeploying(false);
  };

  const handleFeedback = async (action) => {
    try {
      await strategyApi.recordFeedback(strategy.strategy_id, action);
      setFeedbackStatus(action);
    } catch (err) {
      console.error("Feedback failed", err);
    }
  };

  return (
    <div className="flex flex-col h-full p-6 bg-white dark:bg-dark-card rounded-xl border border-slate-200 dark:border-dark-border hover:shadow-lg hover:border-primary-200 dark:hover:border-primary-900 transition-all duration-300">
      
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <span className={`px-3 py-1 text-xs font-bold rounded-full uppercase tracking-wider ${
          strategy.priority_score > 80 
            ? 'bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-400' 
            : 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
        }`}>
          {strategy.strategy_type.replace('_', ' ')}
        </span>
        <div className="text-right">
          <p className="text-xs text-slate-500 dark:text-dark-muted font-medium">Est. Revenue</p>
          <p className="text-lg font-display font-bold text-secondary-600 dark:text-secondary-500">
            +${Math.round(strategy.estimated_revenue).toLocaleString()}
          </p>
        </div>
      </div>

      {/* Content */}
      <h3 className="text-xl font-display font-bold text-slate-900 dark:text-white mb-2">
        {strategy.strategy_name}
      </h3>
      <p className="text-sm text-slate-600 dark:text-slate-300 flex-grow mb-6 leading-relaxed">
        {strategy.description}
      </p>

      {/* Footer Actions */}
      <div className="mt-auto pt-4 border-t border-slate-100 dark:border-dark-border flex items-center justify-between gap-3">
        
        {/* Deploy Button */}
        <button
          onClick={handleDeploy}
          disabled={deploying}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-sm font-medium shadow-sm transition-colors disabled:opacity-70"
        >
          {deploying ? (
            <span className="animate-pulse">Deploying...</span>
          ) : (
            <>
              <span>🚀</span> Deploy to Klaviyo
            </>
          )}
        </button>

        {/* Feedback Loop */}
        <div className="flex gap-1">
          <button 
            onClick={() => handleFeedback('approve')}
            disabled={feedbackStatus !== null}
            className={`p-2.5 rounded-lg transition-colors border ${
              feedbackStatus === 'approve'
                ? 'bg-green-100 text-green-700 border-green-200'
                : 'bg-white dark:bg-dark-bg text-slate-400 hover:text-green-600 border-slate-200 dark:border-dark-border'
            }`}
            title="Approve Strategy"
          >
            👍
          </button>
          <button 
            onClick={() => handleFeedback('reject')}
            disabled={feedbackStatus !== null}
            className={`p-2.5 rounded-lg transition-colors border ${
              feedbackStatus === 'reject'
                ? 'bg-red-100 text-red-700 border-red-200'
                : 'bg-white dark:bg-dark-bg text-slate-400 hover:text-red-600 border-slate-200 dark:border-dark-border'
            }`}
            title="Reject Strategy"
          >
            👎
          </button>
        </div>
      </div>
    </div>
  );
};

export default ActionCard;