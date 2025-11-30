import { ExternalLink } from 'lucide-react';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  sources?: Array<{ title: string; url: string }>;
  timestamp: Date;
}

interface ChatMessageProps {
  message: Message;
}

function ChatMessage({ message }: ChatMessageProps) {
  if (message.sender === 'user') {
    return (
      <div className="flex justify-end">
        <div className="max-w-[75%]">
          <div className="bg-gradient-to-r from-emerald-600 to-emerald-500 text-white rounded-3xl rounded-tr-lg px-5 py-3 shadow-lg">
            <p className="text-sm sm:text-base leading-relaxed">{message.text}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start">
      <div className="max-w-[80%]">
        <div className="bg-white/70 backdrop-blur-md text-gray-800 rounded-3xl rounded-tl-lg px-5 py-3 shadow-lg border border-white/60">
          <p className="text-sm sm:text-base leading-relaxed">{message.text}</p>
        </div>

        {message.sources && message.sources.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {message.sources.map((source, index) => (
              <a
                key={index}
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="group inline-flex items-center gap-1.5 bg-gradient-to-r from-emerald-500/20 to-teal-500/20 backdrop-blur-sm hover:from-emerald-500/30 hover:to-teal-500/30 text-emerald-700 px-3 py-1.5 rounded-full text-xs sm:text-sm font-medium transition-all duration-300 border border-emerald-300/40 hover:border-emerald-400/60 shadow-sm hover:shadow-md"
              >
                <ExternalLink className="w-3 h-3 group-hover:scale-110 transition-transform" />
                <span>{source.title}</span>
              </a>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default ChatMessage;
