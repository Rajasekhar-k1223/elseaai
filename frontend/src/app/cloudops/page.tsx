"use client";

import { Cloud, DollarSign, TrendingUp } from "lucide-react";

export default function CloudOpsPage() {
  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center">
            <Cloud className="w-8 h-8 text-sky-500 mr-3" />
            CloudOps AI
          </h1>
          <p className="text-slate-400 mt-1">Billing analysis, resource recommendations, and cost insights.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6">
           <h2 className="text-xl font-semibold text-white mb-4">AI Cost Insights</h2>
           <div className="space-y-4">
              <div className="p-4 bg-slate-800 border border-slate-700 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center">
                     <TrendingUp className="w-5 h-5 text-red-400 mr-2" />
                     <h3 className="font-medium text-white">AWS EC2 Cost Spike Detected</h3>
                  </div>
                  <span className="text-xs text-slate-400">2 hours ago</span>
                </div>
                <p className="text-sm text-slate-300 leading-relaxed">
                  <strong>AI Analysis:</strong> Billing data indicates a 45% increase in compute costs over the last 48 hours in `us-east-1`. This correlates with 12 new `m5.4xlarge` instances launched by the `data-science-team` role. Recommended action: Ensure these instances are terminated after the model training job completes, or switch to Spot Instances for a projected savings of $420/day.
                </p>
              </div>
           </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center mb-4">
            <DollarSign className="w-6 h-6 text-green-500 mr-2" />
            <h2 className="text-xl font-semibold text-white">Potential Savings</h2>
          </div>
          <p className="text-4xl font-bold text-white mt-4">$1,240<span className="text-sm text-slate-400 font-normal"> / month</span></p>
          <p className="text-slate-400 mt-2 text-sm">Based on current AI recommendations across AWS and Azure.</p>
        </div>
      </div>
    </div>
  );
}
