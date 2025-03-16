import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, Search, Filter, User, BookOpen, AlignLeft, ChevronDown, ChevronUp, X } from 'lucide-react';
import './App.css';

function App() {
  const [courtType, setCourtType] = useState('High Court');
  const [filters, setFilters] = useState({
    caseNo: '',
    crimeNo: '',
    keyword: '',
    petitioner: '',
    lawyer: '',
    judge: '',
    location: '',
    timeframe: ''
  });
  const [cases, setCases] = useState([]);
  const [expandedCases, setExpandedCases] = useState(new Set());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [chatOpen, setChatOpen] = useState(false);
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const chatContainerRef = useRef(null);
  const [showFilters, setShowFilters] = useState(true);

  const highlightText = (text, searchTerms) => {
    if (!text) return text;
    
    // Create an array of non-empty filter values with their types
    const activeFilters = Object.entries(searchTerms).filter(([_, value]) => value.trim() !== '');
    
    if (activeFilters.length === 0) return text;

    // Create patterns for different types of content
    const createPattern = (type, value) => {
      const escapedValue = value.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
      switch (type) {
        case 'judge':
          return `(THE HONOURABLE (?:MR|MS|MRS)?\\.? JUSTICE\\s+${escapedValue}|JUSTICE\\s+${escapedValue}|${escapedValue})`;
        case 'lawyer':
          return `(ADVOCATE\\s+${escapedValue}|${escapedValue})`;
        case 'caseNo':
          return `(CASE\\s+NO\\.?\\s*${escapedValue}|${escapedValue})`;
        case 'crimeNo':
          return `(CRIME\\s+NO\\.?\\s*${escapedValue}|${escapedValue})`;
        default:
          return escapedValue;
      }
    };

    let processedText = text;
    let lastIndex = 0;
    const segments = [];

    // Sort filters by length (longest first) to handle overlapping matches
    activeFilters.sort((a, b) => b[1].length - a[1].length);

    // Create a single regex pattern that includes all active filters
    const patterns = activeFilters.map(([type, value]) => createPattern(type, value));
    const combinedPattern = new RegExp(patterns.join('|'), 'gi');

    // Find all matches and their positions
    const matches = Array.from(processedText.matchAll(combinedPattern));
    
    matches.forEach((match, index) => {
      // Add text before the match
      if (match.index > lastIndex) {
        segments.push(processedText.slice(lastIndex, match.index));
      }

      // Determine the filter type for this match
      const filterType = activeFilters.find(([_, value]) => 
        match[0].toLowerCase().includes(value.toLowerCase())
      )?.[0] || 'keyword';

      // Add the highlighted match
      segments.push(
        <mark 
          key={`highlight-${index}`}
          className={`highlight-${filterType}`}
          title={`Matched ${filterType}`}
        >
          {match[0]}
        </mark>
      );

      lastIndex = match.index + match[0].length;
    });

    // Add any remaining text
    if (lastIndex < processedText.length) {
      segments.push(processedText.slice(lastIndex));
    }

    return <>{segments}</>;
  };

  const toggleExpandCase = (index) => {
    setExpandedCases(prev => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };

  const handleApplyFilters = async () => {
    // Check if at least one filter is filled
    const hasActiveFilters = Object.values(filters).some(value => value.trim() !== '');
    if (!hasActiveFilters) {
      setError('Please enter at least one search criteria');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5000/search-cases', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          courtType,
          ...filters
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch cases');
      }

      const data = await response.json();
      if (data.status === 'success' && Array.isArray(data.cases)) {
        setCases(data.cases);
        setExpandedCases(new Set());
        if (data.cases.length === 0) {
          setError('No cases found matching your criteria');
        }
      } else {
        setError('Invalid response from server');
      }
    } catch (error) {
      console.error('Error fetching cases:', error);
      setError('Error fetching cases. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMessage = chatInput.trim();
    setChatInput('');
    
    // Add user message to chat history
    setChatHistory(prev => [...prev, { type: 'user', content: userMessage }]);
    setIsChatLoading(true);

    try {
      const response = await fetch('http://localhost:5000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: userMessage }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      
      // Format the cases into a readable response
      if (data.cases && Array.isArray(data.cases)) {
        const formattedResponse = data.cases.map((caseText, index) => 
          `Case ${index + 1}:\n${caseText.slice(0, 300)}...`
        ).join('\n\n');
        
        setChatHistory(prev => [...prev, { 
          type: 'assistant', 
          content: formattedResponse || 'No relevant cases found for your query.'
        }]);
      } else {
        throw new Error('Invalid response format');
      }
    } catch (error) {
      console.error('Chat error:', error);
      setChatHistory(prev => [...prev, { 
        type: 'assistant', 
        content: 'Sorry, I encountered an error processing your request. Please try again.' 
      }]);
    } finally {
      setIsChatLoading(false);
    }
  };

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatHistory]);

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 font-sans">
      {/* Header */}
      <header className="sticky top-0 z-10 w-full bg-gradient-to-r from-indigo-600 to-blue-600 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BookOpen className="h-8 w-8 text-white" />
              </div>
              <h1 className="ml-3 text-2xl md:text-3xl font-bold text-white">
                Legal Knowledge Hub
              </h1>
            </div>
            <div className="hidden md:block">
              <div className="text-sm text-indigo-100">
                Advanced Legal Document Search & Analysis
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 container mx-auto px-4 py-8 max-w-5xl">
        {/* Intro Section */}
        <div className="mb-8 text-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-3">Search Legal Documents</h2>
          <p className="text-gray-600 max-w-3xl mx-auto">
            Access and analyze court cases with precision filtering and AI-powered search capabilities.
          </p>
        </div>

        {/* Court Type Selection */}
        <div className="bg-white rounded-xl shadow-md p-6 mb-6 transition-all duration-300 hover:shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-gray-800 flex items-center">
              <BookOpen className="w-5 h-5 mr-2 text-indigo-600" />
              Court Type
            </h3>
          </div>
          <select
            className="w-full p-3 border border-gray-200 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all bg-white shadow-sm text-gray-700"
            value={courtType}
            onChange={(e) => setCourtType(e.target.value)}
          >
            <option value="High Court">High Court</option>
            <option value="District Court">District Court</option>
            <option value="Supreme Court">Supreme Court</option>
          </select>
        </div>

        {/* Search Filters */}
        <div className="bg-white rounded-xl shadow-md overflow-hidden mb-6 transition-all duration-300 hover:shadow-lg">
          <div 
            className="p-6 cursor-pointer" 
            onClick={() => setShowFilters(!showFilters)}
          >
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-semibold text-gray-800 flex items-center">
                <Filter className="w-5 h-5 mr-2 text-indigo-600" />
                Search Filters
              </h3>
              <button 
                className="p-2 rounded-md hover:bg-indigo-50 transition-colors"
                aria-label="Toggle filters"
              >
                {showFilters ? 
                  <ChevronUp className="w-5 h-5 text-indigo-600" /> : 
                  <ChevronDown className="w-5 h-5 text-indigo-600" />
                }
              </button>
            </div>
          </div>
          
          <div className={`px-6 pb-6 ${showFilters ? 'block' : 'hidden'}`}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {Object.keys(filters).map((key) => (
                <div key={key} className="flex flex-col">
                  <label className="text-sm font-medium text-gray-700 mb-1 flex items-center">
                    {key === 'petitioner' && <User className="w-4 h-4 mr-1 text-indigo-500" />}
                    {key === 'lawyer' && <User className="w-4 h-4 mr-1 text-indigo-500" />}
                    {key === 'judge' && <User className="w-4 h-4 mr-1 text-indigo-500" />}
                    {key === 'caseNo' && <AlignLeft className="w-4 h-4 mr-1 text-indigo-500" />}
                    {key === 'crimeNo' && <AlignLeft className="w-4 h-4 mr-1 text-indigo-500" />}
                    {key.replace(/([A-Z])/g, ' $1').toLowerCase().charAt(0).toUpperCase() + 
                     key.replace(/([A-Z])/g, ' $1').toLowerCase().slice(1)}
                  </label>
                  <div className="relative rounded-md shadow-sm">
                    <input
                      className="p-3 border border-gray-200 rounded-lg w-full focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all text-gray-700"
                      placeholder={`Enter ${key.replace(/([A-Z])/g, ' $1').toLowerCase()}`}
                      value={filters[key]}
                      onChange={(e) => setFilters((prev) => ({ ...prev, [key]: e.target.value }))}
                    />
                    {filters[key] && (
                      <button 
                        className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                        onClick={() => setFilters((prev) => ({ ...prev, [key]: '' }))}
                      >
                        <X className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
            <button 
              onClick={handleApplyFilters}
              className="mt-6 w-full bg-gradient-to-r from-indigo-600 to-blue-600 text-white flex items-center justify-center space-x-2 p-3 rounded-lg hover:from-indigo-700 hover:to-blue-700 transition-all shadow-md disabled:opacity-50 font-medium"
              disabled={loading}
            >
              {loading ? (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                  <span>Searching...</span>
                </div>
              ) : (
                <>
                  <Search className="w-5 h-5" />
                  <span>Apply Filters</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 mb-6 animate-fade-in">
            <div className="flex items-center">
              <svg className="w-5 h-5 mr-2 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              {error}
            </div>
          </div>
        )}

        {/* Search Results */}
        {cases.length > 0 && (
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">Search Results ({cases.length})</h3>
          </div>
        )}

        <div className="space-y-6">
          {cases.map((caseText, index) => (
            <div 
              key={index}
              className="bg-white rounded-xl shadow-md p-6 transition-all hover:shadow-lg border border-gray-100"
            >
              <div className="prose max-w-none">
                <div className="case-text text-gray-700 text-sm leading-relaxed whitespace-pre-line">
                  {highlightText(
                    expandedCases.has(index) ? caseText : caseText.slice(0, 500),
                    filters
                  )}
                  {caseText.length > 500 && !expandedCases.has(index) && (
                    <>
                      <div className="text-gray-400 mt-2">...</div>
                      <button
                        className="mt-3 text-indigo-600 hover:text-indigo-800 font-medium inline-flex items-center space-x-0.5 bg-indigo-50 hover:bg-indigo-100 rounded-full py-0.5 px-2 text-xs transition-all duration-200 group"
                        onClick={() => toggleExpandCase(index)}
                      >
                        <span>Show More</span>
                        <svg className="w-2.5 h-2.5 transform group-hover:translate-y-0.5 transition-transform" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M19 9l-7 7-7-7" />
                        </svg>
                      </button>
                    </>
                  )}
                  {expandedCases.has(index) && (
                    <button
                      className="mt-3 text-indigo-600 hover:text-indigo-800 font-medium inline-flex items-center space-x-0.5 bg-indigo-50 hover:bg-indigo-100 rounded-full py-0.5 px-2 text-xs transition-all duration-200 group"
                      onClick={() => toggleExpandCase(index)}
                    >
                      <span>Show Less</span>
                      <svg className="w-2.5 h-2.5 transform group-hover:-translate-y-0.5 transition-transform" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M5 15l7-7 7 7" />
                      </svg>
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* No Results Message */}
        {cases.length === 0 && !loading && !error && (
          <div className="bg-white rounded-xl shadow-md p-8 text-center">
            <div className="flex flex-col items-center justify-center">
              <Search className="w-12 h-12 text-indigo-200 mb-4" />
              <h3 className="text-xl font-semibold text-gray-800 mb-2">No Cases Found</h3>
              <p className="text-gray-500">Apply filters to search for legal cases</p>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8 mt-12">
        <div className="container mx-auto px-4 md:px-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h4 className="text-lg font-semibold mb-4 flex items-center">
                <BookOpen className="w-5 h-5 mr-2" />
                Legal Knowledge Hub
              </h4>
              <p className="text-gray-300 text-sm">
                Advanced search and analysis platform for legal professionals.
              </p>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Features</h4>
              <ul className="text-gray-300 text-sm space-y-2">
                <li>Precise document search</li>
                <li>Intelligent filtering</li>
                <li>AI-powered assistance</li>
                <li>Court case analysis</li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Contact</h4>
              <p className="text-gray-300 text-sm">
                For support or inquiries, please contact our team.
              </p>
              <div className="mt-4">
                <a href="#" className="text-indigo-400 hover:text-indigo-300 text-sm">
                  support@legalknowledgehub.com
                </a>
              </div>
            </div>
          </div>
          <div className="border-t border-gray-700 mt-8 pt-8 text-center text-gray-400 text-sm">
            © {new Date().getFullYear()} Legal Knowledge Hub. All rights reserved.
          </div>
        </div>
      </footer>

      {/* Chat Button */}
      <button
        className="fixed bottom-6 right-6 bg-gradient-to-r from-indigo-600 to-blue-600 text-white p-4 rounded-full shadow-lg hover:shadow-xl transition-all transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 z-50"
        onClick={() => setChatOpen(!chatOpen)}
        aria-label="Chat with AI Assistant"
      >
        <MessageSquare className="w-6 h-6" />
      </button>

      {/* Chat Panel */}
      {chatOpen && (
        <div className="fixed bottom-24 right-6 bg-white w-96 rounded-xl shadow-2xl overflow-hidden animate-slide-up z-50 border border-gray-200">
          <div className="p-4 bg-gradient-to-r from-indigo-600 to-blue-600">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-lg font-semibold text-white">AI Legal Assistant</h2>
                <p className="text-sm text-indigo-100">Ask questions about legal documents</p>
              </div>
              <button 
                onClick={() => setChatOpen(false)}
                className="text-white hover:text-indigo-200 focus:outline-none"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>
          
          <div 
            ref={chatContainerRef}
            className="h-96 overflow-y-auto p-4 space-y-4 bg-gray-50"
          >
            {chatHistory.length === 0 && (
              <div className="flex justify-center items-center h-full text-center px-6">
                <div className="text-gray-400">
                  <MessageSquare className="w-10 h-10 mx-auto mb-3 text-indigo-200" />
                  <p className="text-sm">Ask any question about legal cases and documents.</p>
                  <p className="text-xs mt-2">Examples: "Find cases involving property disputes" or "Show me recent judgments by Justice Kumar"</p>
                </div>
              </div>
            )}
            
            {chatHistory.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl p-3.5 shadow-sm ${
                    message.type === 'user'
                      ? 'bg-indigo-600 text-white rounded-br-none'
                      : 'bg-white text-gray-800 rounded-bl-none border border-gray-100'
                  }`}
                >
                  <div className="whitespace-pre-line text-sm">
                    {message.content}
                  </div>
                  <div 
                    className={`text-right text-xs mt-1 ${
                      message.type === 'user' ? 'text-indigo-200' : 'text-gray-400'
                    }`}
                  >
                    {new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                  </div>
                </div>
              </div>
            ))}
            
            {isChatLoading && (
              <div className="flex justify-start">
                <div className="bg-white rounded-2xl p-4 rounded-bl-none shadow-sm border border-gray-100">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            )}
          </div>

          <form onSubmit={handleChatSubmit} className="p-4 border-t border-gray-200 bg-white">
            <div className="flex space-x-2">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Type your question here..."
                className="flex-1 p-3 border border-gray-200 rounded-lg focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-gray-700"
              />
              <button
                type="submit"
                disabled={isChatLoading}
                className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 flex items-center justify-center"
              >
                <span className="mr-1">Send</span>
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

export default App;
