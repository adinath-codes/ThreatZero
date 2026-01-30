import { CardDescription, CardTitle } from "@/components/ui/card";

const RiskGauge = ({ score = 70 }) => {
  const segments = 24;
  const activeSegments = Math.round((score / 100) * segments);

  return (
      <div className="w-full  flex flex-col">
        <div >
            
<h1 className="text-xl font-bold">Risk Gauge</h1>
<p className="text-xs font-medium text-gray-400">ratio of attacks to normal activity</p>
        </div>
    
    <div className="flex justify-center items-center mt-10">

    <div className="relative flex items-center  justify-center  w-full h-32 sm:w-40 sm:h-40 md:w-48 md:h-48">
        {/* <div className="">
        <h1 className="text-xl font-bold">Attacks Timeline</h1>
        <p className="text-xs font-medium text-gray-400">This week</p>
      </div> */}
      

      <svg className="transform -rotate-90 w-full h-full" viewBox="0 0 160 160">
        {[...Array(segments)].map((_, i) => {
          const isActive = i < activeSegments;
          const rotation = (i * 360) / segments;
          
          return (
            <rect
              key={i}
              x="145"
              y="76"
              width="12"
              height="8"
              rx="2"
              fill={isActive ? "#d946ef" : "#1f1f23"}
              transform={`rotate(${rotation}, 80, 80)`}
              className="transition-colors duration-500"
            />
          );
        })}
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="text-[10px] sm:text-xs text-gray-400 uppercase tracking-widest">Score</span>
        <span className="text-2xl sm:text-4xl font-bold text-white">{score}%</span>
      </div>
      </div>

    </div>
   
    </div>
  );
};
export default RiskGauge;