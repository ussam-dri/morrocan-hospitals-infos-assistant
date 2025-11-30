function LoadingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="bg-white/70 backdrop-blur-md rounded-3xl rounded-tl-lg px-6 py-4 shadow-lg border border-white/60">
        <div className="flex items-center gap-3">
          <div className="flex gap-1.5">
            <div className="w-2.5 h-2.5 bg-emerald-500 rounded-full animate-pulse"></div>
            <div className="w-2.5 h-2.5 bg-emerald-500 rounded-full animate-pulse animation-delay-200"></div>
            <div className="w-2.5 h-2.5 bg-emerald-500 rounded-full animate-pulse animation-delay-400"></div>
          </div>
          <div className="relative w-24 h-1 bg-gray-200/50 rounded-full overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-emerald-500 to-teal-500 animate-heartbeat origin-left"></div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoadingIndicator;
