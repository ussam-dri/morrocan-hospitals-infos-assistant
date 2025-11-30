import { useState, useRef, useEffect } from 'react';
import { Send, Stethoscope, Globe } from 'lucide-react';
import AnimatedBackground from './components/AnimatedBackground';
import ChatMessage from './components/ChatMessage';
import LoadingIndicator from './components/LoadingIndicator';

type Language = 'fr' | 'ar' | 'en';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  sources?: Array<{ title: string; url: string }>;
  timestamp: Date;
}

const translations = {
  fr: {
    welcome: 'Bonjour ! Je suis votre assistant médical IA pour le Maroc. Demandez-moi des informations sur les cliniques, les médecins ou les hôpitaux.',
    placeholder: 'Posez des questions sur les médecins, cliniques ou hôpitaux...',
    title: 'Assistant Médical IA Marocain',
    subtitle: 'Votre compagnon de santé de confiance',
    error: 'Désolé, j\'ai des difficultés à me connecter.',
  },
  ar: {
    welcome: 'مرحبا! أنا مساعدك الطبي الذكي للمغرب. اسألني عن العيادات أو الأطباء أو المستشفيات.',
    placeholder: 'اسأل عن الأطباء أو العيادات أو المستشفيات...',
    title: 'المساعد الطبي الذكي المغربي',
    subtitle: 'رفيقك الصحي الموثوق',
    error: 'عذراً، أواجه مشكلة في الاتصال.',
  },
  en: {
    welcome: 'Hello! I am your AI Health Assistant for Morocco. Ask me about clinics, doctors, or hospitals.',
    placeholder: 'Ask about doctors, clinics, or hospitals...',
    title: 'Moroccan Medical AI Assistant',
    subtitle: 'Your trusted health companion',
    error: 'Sorry, I am having trouble connecting.',
  },
};

function App() {
  const [language, setLanguage] = useState<Language>('fr');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: translations.fr.welcome,
      sender: 'ai',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showLanguageMenu, setShowLanguageMenu] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const languageMenuRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Update welcome message when language changes
    setMessages((prev) => {
      const newMessages = [...prev];
      const welcomeMsg = newMessages.find((m) => m.id === '1');
      if (welcomeMsg) {
        welcomeMsg.text = translations[language].welcome;
      }
      return newMessages;
    });
  }, [language]);

  useEffect(() => {
    // Close language menu when clicking outside
    const handleClickOutside = (event: MouseEvent) => {
      if (languageMenuRef.current && !languageMenuRef.current.contains(event.target as Node)) {
        setShowLanguageMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: inputValue, language: language }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: data.response || data.message || 'I received your message.',
        sender: 'ai',
        sources: data.sources,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: translations[language].error,
        sender: 'ai',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      <AnimatedBackground />

      <div className="relative z-10 min-h-screen flex items-center justify-center p-4 sm:p-6 lg:p-8">
        <div className="w-full max-w-4xl h-[85vh] backdrop-blur-2xl bg-white/30 rounded-3xl shadow-2xl border border-white/40 flex flex-col overflow-hidden">
          <div className="bg-gradient-to-r from-emerald-600/80 to-teal-600/80 backdrop-blur-sm px-6 py-4 flex items-center justify-between border-b border-white/20">
            <div className="flex items-center gap-3">
              <div className="bg-white/20 p-2 rounded-xl backdrop-blur-sm">
                <Stethoscope className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-white font-semibold text-lg">{translations[language].title}</h1>
                <p className="text-white/80 text-xs">{translations[language].subtitle}</p>
              </div>
            </div>
            <div className="relative" ref={languageMenuRef}>
              <button
                onClick={() => setShowLanguageMenu(!showLanguageMenu)}
                className="bg-white/20 hover:bg-white/30 backdrop-blur-sm px-4 py-2 rounded-lg text-white font-medium text-sm flex items-center gap-2 transition-all duration-300 border border-white/30 hover:border-white/50"
                title="Switch language"
              >
                <Globe className="w-4 h-4" />
                <span className="uppercase">{language}</span>
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              {showLanguageMenu && (
                <div className="absolute right-0 mt-2 w-32 bg-white/95 backdrop-blur-md rounded-lg shadow-xl border border-white/40 overflow-hidden z-50">
                  {(['fr', 'ar', 'en'] as Language[]).map((lang) => (
                    <button
                      key={lang}
                      onClick={() => {
                        setLanguage(lang);
                        setShowLanguageMenu(false);
                      }}
                      className={`w-full px-4 py-2 text-left text-sm transition-colors ${
                        language === lang
                          ? 'bg-emerald-500/20 text-emerald-700 font-semibold'
                          : 'text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      <span className="uppercase font-medium">{lang}</span>
                      {lang === 'fr' && <span className="ml-2 text-xs text-gray-500">Français</span>}
                      {lang === 'ar' && <span className="ml-2 text-xs text-gray-500">العربية</span>}
                      {lang === 'en' && <span className="ml-2 text-xs text-gray-500">English</span>}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isLoading && <LoadingIndicator />}
            <div ref={messagesEndRef} />
          </div>

          <div className="p-4 sm:p-6">
            <div className="bg-white/60 backdrop-blur-xl rounded-full shadow-lg border border-white/60 flex items-center gap-3 px-4 sm:px-6 py-3 hover:shadow-xl transition-shadow duration-300">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={translations[language].placeholder}
                className="flex-1 bg-transparent outline-none text-gray-800 placeholder-gray-500 text-sm sm:text-base"
                disabled={isLoading}
              />
              <button
                onClick={handleSend}
                disabled={isLoading || !inputValue.trim()}
                className="bg-gradient-to-r from-emerald-600 to-teal-600 text-white p-2.5 sm:p-3 rounded-full hover:from-emerald-700 hover:to-teal-700 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                <Send className="w-4 h-4 sm:w-5 sm:h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
