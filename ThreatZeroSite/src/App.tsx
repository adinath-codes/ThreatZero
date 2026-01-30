import React, { useState, useEffect } from 'react';
import { 
  LayoutDashboard, 
  ShieldAlert, 
  Search, 
  Bell, 
  Menu, 
  X,
  ChevronDown, 
  Activity,
  Server,
  Cloud,
  Lock,
  Zap,
  Box,
  Globe,
  Database,
  User,
  ExternalLink
} from 'lucide-react';
import {fetchLogs,fetchRisks} from "./apis"
// --- Components ---
import BarChartCard from './comp/BarChartCard';
import RiskGauge from './comp/RiskChartCard';
import PieChartCard from './comp/PieChartCard';
/**
 * Stats Card component for the top section.
 */
const StatCard = ({ title, value, subValue, icon: Icon, color, trend }) => {
  return (
    <div className="bg-[#16161a] border border-[#232329] rounded-2xl p-4 sm:p-6 flex flex-col justify-between hover:border-fuchsia-500/50 transition-all cursor-default">
      <div className="flex justify-between items-start">
        <div className={`p-2 sm:p-3 rounded-xl bg-opacity-10 ${color}`}>
          <Icon className={`w-4 h-4 sm:w-5 sm:h-5 ${color.replace('bg-', 'text-')}`} />
        </div>
        <span className="text-[10px] sm:text-xs font-medium text-gray-500">{subValue}</span>
      </div>
      <div className="mt-4">
        <h3 className="text-xs sm:text-sm text-gray-400 mb-1">{title}</h3>
        <div className="flex items-baseline gap-3">
          <span className="text-2xl sm:text-3xl font-bold text-white">{value}</span>
          {trend && (
             <div className="h-8 sm:h-12 w-16 sm:w-24 relative overflow-hidden">
                <svg viewBox="0 0 100 40" className="absolute bottom-0 left-0 w-full h-full">
                  <path 
                    d={trend} 
                    fill="none" 
                    stroke="#d946ef" 
                    strokeWidth="2" 
                    strokeLinecap="round" 
                  />
                </svg>
             </div>
          )}
        </div>
      </div>
    </div>
  );
};

/**
 * Main Table for Attack Surface Overview
 */
const AttackSurfaceTable = ({ data }) => {
  return (
    <div className="overflow-x-auto -mx-4 sm:mx-0">
      <div className="inline-block min-w-full align-middle p-4 sm:p-0">
        <table className="w-full text-left border-separate border-spacing-y-2">
          <thead>
            <tr className="text-gray-500 text-[10px] sm:text-xs uppercase tracking-wider">
              <th className="px-3 sm:px-4 py-2 font-medium">Name</th>
              <th className="px-3 sm:px-4 py-2 font-medium hidden md:table-cell">Connector</th>
              <th className="px-3 sm:px-4 py-2 font-medium hidden sm:table-cell">Workload</th>
              <th className="px-3 sm:px-4 py-2 font-medium">Security Score</th>
              <th className="px-3 sm:px-4 py-2 font-medium hidden lg:table-cell">Date</th>
              <th className="px-3 sm:px-4 py-2 font-medium text-right">Perms</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr key={idx} className="bg-[#16161a] hover:bg-[#1c1c21] transition-colors group cursor-pointer">
                <td className="px-3 sm:px-4 py-3 sm:py-4 rounded-l-xl">
                  <div className="flex items-center gap-2 sm:gap-3">
                    <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-[#232329] flex items-center justify-center text-fuchsia-400 shrink-0">
                      {row.type === 'VM' ? <Server size={14}/> : <Box size={14}/>}
                    </div>
                    <div className="min-w-0">
                      <div className="text-xs sm:text-sm font-semibold text-white group-hover:text-fuchsia-400 transition-colors truncate max-w-[120px] sm:max-w-none">
                        {row.name}
                      </div>
                      <div className="text-[9px] sm:text-[10px] text-gray-500 uppercase tracking-tight truncate">
                        {row.category}
                      </div>
                    </div>
                  </div>
                </td>
                <td className="px-3 sm:px-4 py-3 sm:py-4 hidden md:table-cell">
                  <div className="flex items-center gap-2 text-xs text-gray-300">
                    <Cloud size={14} className="text-blue-400 shrink-0"/>
                    <span className="truncate">{row.connector}</span>
                  </div>
                </td>
                <td className="px-3 sm:px-4 py-3 sm:py-4 hidden sm:table-cell">
                   <div className="flex items-center gap-2 text-xs text-gray-300">
                     <div className="w-2 h-2 rounded-full bg-orange-500 shrink-0"></div>
                     <span className="truncate">{row.workload}</span>
                   </div>
                </td>
                <td className="px-3 sm:px-4 py-3 sm:py-4">
                  <div className="flex items-center gap-2 sm:gap-3">
                    <div className="w-16 sm:w-24 md:w-32 h-1.5 bg-[#232329] rounded-full overflow-hidden shrink-0">
                      <div 
                        className="h-full bg-gradient-to-r from-fuchsia-600 to-purple-400 rounded-full"
                        style={{ width: `${row.score}%` }}
                      />
                    </div>
                    <span className="text-[10px] sm:text-xs text-gray-400">{row.score}%</span>
                  </div>
                </td>
                <td className="px-3 sm:px-4 py-3 sm:py-4 text-[10px] sm:text-xs text-gray-400 hidden lg:table-cell whitespace-nowrap">
                  {row.date}
                </td>
                <td className="px-3 sm:px-4 py-3 sm:py-4 rounded-r-xl text-right">
                  <div className="flex gap-1 justify-end">
                     {[...Array(row.type === 'VM' ? 3 : 2)].map((_, i) => (
                       <div key={i} className="w-5 h-5 rounded bg-[#232329] flex items-center justify-center">
                          <Lock size={10} className="text-gray-500" />
                       </div>
                     ))}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// --- Main Application ---

export default function App() {
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  
  const tableData = [
    { name: "amazonSageMarket", category: "Compute | VM", connector: "Cyscale GCP", workload: "gen2-event", score: 25, date: "Apr 12, 2025", type: 'VM' },
    { name: "id-sap-service", category: "Compute | VM", connector: "Sandbox", workload: "Test Notebook", score: 55, date: "Apr 14, 2025", type: 'VM' },
    { name: "arnilas-01-42578", category: "Compute | VM", connector: "Cyscale Sandbox", workload: "fapp-sap-service", score: 43, date: "Apr 15, 2025", type: 'VM' },
    { name: "aks-cyscale-0001", category: "Compute | VM", connector: "Sandbox", workload: "function-1", score: 70, date: "Apr 17, 2025", type: 'VM' },
    { name: "eks-cti-eks-ZIV9K", category: "Compute | VM", connector: "Cyscale Dev env", workload: "neo-eval", score: 61, date: "Apr 18, 2025", type: 'VM' },
    { name: "neo145783657", category: "Compute | VM", connector: "Cyscale GCP", workload: "cyscale-app", score: 39, date: "Apr 19, 2025", type: 'VM' },
    { name: "cyscale-app", category: "Compute | VM", connector: "Cyscale Sandbox", workload: "vulnerable-VM", score: 75, date: "Apr 21, 2025", type: 'VM' },
    { name: "amazonSageMarket", category: "Compute | VM", connector: "Cyscale GCP", workload: "Test Notebook", score: 55, date: "Apr 22, 2025", type: 'VM' },
  ];

  // Close sidebar on larger screens if window is resized
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) setSidebarOpen(false);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div className="min-h-screen bg-[#0d0d0f] text-gray-200 font-sans selection:bg-fuchsia-500/30 overflow-x-hidden">
      
      {/* Sidebar - Desktop Overlay or Hidden */}
      <div className={`fixed inset-0 bg-black/60 z-[60] lg:hidden transition-opacity duration-300 ${isSidebarOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`} onClick={() => setSidebarOpen(false)} />
      
      <aside className={`fixed left-0 top-0 h-full w-20 border-r border-[#1a1a1e] bg-[#0d0d0f] flex flex-col items-center py-8 z-[70] transition-transform duration-300 lg:translate-x-0 ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}>
        <div className="mb-12">
          <div className="w-10 h-10 bg-fuchsia-600 rounded-xl flex items-center justify-center shadow-lg shadow-fuchsia-900/20">
            <Zap className="text-white fill-current" />
          </div>
        </div>
        
        <nav className="flex flex-col gap-8">
          <button className="p-3 text-fuchsia-500 bg-fuchsia-500/10 rounded-xl"><LayoutDashboard size={24}/></button>
          <button className="p-3 text-gray-600 hover:text-gray-300 transition-colors"><ShieldAlert size={24}/></button>
          <button className="p-3 text-gray-600 hover:text-gray-300 transition-colors"><Globe size={24}/></button>
          <button className="p-3 text-gray-600 hover:text-gray-300 transition-colors"><Database size={24}/></button>
          <button className="p-3 text-gray-600 hover:text-gray-300 transition-colors"><User size={24}/></button>
        </nav>
        
        <div className="mt-auto">
          <button className="p-3 text-gray-600 hover:text-gray-300 transition-colors"><ExternalLink size={20}/></button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="lg:pl-20 min-h-screen">
        
        {/* Top Header */}
        <header className="h-16 sm:h-20 border-b border-[#1a1a1e] flex items-center justify-between px-4 sm:px-6 lg:px-10 bg-[#0d0d0f]/80 backdrop-blur-md sticky top-0 z-40">
          <div className="flex items-center gap-3">
             <button 
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 -ml-2 text-gray-400 hover:text-white"
             >
               <Menu size={24} />
             </button>
             <h1 className="text-lg sm:text-xl font-bold text-white tracking-tight">ThreatZero</h1>
             <div className="hidden sm:block h-4 w-[1px] bg-gray-800 mx-2" />
             <div className="hidden sm:flex items-center gap-1 text-sm font-medium text-gray-400">
               Dashboard <ChevronDown size={14} />
             </div>
          </div>

          <div className="flex items-center gap-3 sm:gap-6">
            <div className="relative group hidden md:block">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-600 group-focus-within:text-fuchsia-500 transition-colors" size={18} />
              <input 
                type="text" 
                placeholder="Search endpoints..." 
                className="bg-[#16161a] border border-[#232329] rounded-full py-2 pl-10 pr-4 text-sm w-48 lg:w-64 xl:w-80 focus:outline-none focus:border-fuchsia-500/50 transition-all placeholder:text-gray-700"
              />
            </div>
            
            <button className="md:hidden p-2 text-gray-400">
               <Search size={20} />
            </button>

            <button className="relative p-2 text-gray-400 hover:text-white transition-colors">
              <Bell size={20} />
              <span className="absolute top-1 right-1 w-2 h-2 bg-fuchsia-500 rounded-full border-2 border-[#0d0d0f]" />
            </button>

            <div className="flex items-center gap-3 sm:pl-6 sm:border-l border-[#232329]">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-fuchsia-600 to-indigo-600 flex items-center justify-center text-[10px] font-bold text-white uppercase shrink-0">
                JD
              </div>
            </div>
          </div>
        </header>

        {/* Dashboard Content */}
        <div className="p-4 sm:p-6 lg:p-8 xl:p-10 w-full mx-auto">
          
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
            <h2 className="text-xl sm:text-2xl font-bold text-white">Your Attack Surface</h2>
            <div className="flex items-center gap-2 sm:gap-3">
               <div className="px-3 sm:px-4 py-2 bg-[#16161a] border border-[#232329] rounded-lg text-xs font-medium text-gray-400 flex items-center gap-2 cursor-pointer hover:bg-[#232329]">
                 Daily <ChevronDown size={14} />
               </div>
               <button className="flex-1 sm:flex-none px-3 sm:px-4 py-2 bg-fuchsia-600 hover:bg-fuchsia-700 text-white rounded-lg text-xs font-bold transition-colors whitespace-nowrap">
                 Generate Report
               </button>
            </div>
          </div>

          {/* Top Cards Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6 mb-10">
           <BarChartCard/>
            
            
            
            <PieChartCard/>
            <StatCard 
              title="Image file risk" 
              value="46%" 
              subValue="High" 
              icon={Box} 
              color="bg-orange-500" 
              trend="M0 30 L10 25 L20 30 L30 10 L40 25 L50 30 L60 20 L70 30 L80 15 L90 35 L100 25"
            />
            <div className="bg-[#16161a] border border-[#232329] rounded-2xl p-4 sm:p-6 flex  relative overflow-hidden group min-h-[140px]">
               <RiskGauge score={40} />
               
            </div>
          </div>

          {/* Table Section */}
          <div className="bg-[#0d0d0f]">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
              <h3 className="text-base sm:text-lg font-bold text-white flex items-center gap-3">
                Attack Surface Overview
                <span className="text-[10px] bg-[#16161a] px-2 py-0.5 rounded text-gray-500 font-normal">8 Resources</span>
              </h3>
              <div className="flex gap-4">
                <button className="text-[10px] sm:text-xs text-gray-500 hover:text-white transition-colors">Filters</button>
                <button className="text-[10px] sm:text-xs text-gray-500 hover:text-white transition-colors">Export CSV</button>
              </div>
            </div>
            
            <AttackSurfaceTable data={tableData} />
            
            <div className="mt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-[10px] sm:text-xs text-gray-500 text-center sm:text-left">
              <p>Showing 8 of 142 resources across 4 clusters</p>
              <div className="flex gap-2">
                <button className="w-8 h-8 rounded bg-[#16161a] flex items-center justify-center hover:bg-[#232329] transition-colors">1</button>
                <button className="w-8 h-8 rounded flex items-center justify-center hover:bg-[#16161a] transition-colors">2</button>
                <button className="w-8 h-8 rounded flex items-center justify-center hover:bg-[#16161a] transition-colors">3</button>
                <button className="px-3 h-8 rounded hover:bg-[#16161a] transition-colors">Next</button>
              </div>
            </div>
          </div>

        </div>

        {/* Footer info */}
        <footer className="px-4 sm:px-10 py-8 border-t border-[#1a1a1e] flex flex-col sm:row justify-between items-center gap-4 text-[9px] sm:text-[10px] text-gray-600 uppercase tracking-widest text-center">
          <div>© 2025 ThreatZero Security Systems</div>
          <div className="flex gap-4 sm:gap-6">
             <a href="#" className="hover:text-gray-400">Privacy Policy</a>
             <a href="#" className="hover:text-gray-400">API Documentation</a>
             <a href="#" className="hover:text-gray-400">Support</a>
          </div>
        </footer>
      </main>

      {/* Background decoration elements */}
      <div className="fixed top-0 left-0 w-full h-full pointer-events-none -z-10 overflow-hidden opacity-30">
        <div className="absolute top-[20%] -right-[10%] w-[50%] h-[50%] bg-fuchsia-600/10 blur-[120px] rounded-full" />
        <div className="absolute bottom-[10%] -left-[5%] w-[40%] h-[40%] bg-indigo-600/10 blur-[100px] rounded-full" />
      </div>
    </div>
  );
}