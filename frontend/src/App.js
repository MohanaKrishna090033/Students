import React, { useState, useEffect, useMemo } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Language Context
const LanguageContext = React.createContext();

const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState('english');
  
  const toggleLanguage = () => {
    setLanguage(prev => prev === 'english' ? 'odia' : 'english');
  };
  
  return (
    <LanguageContext.Provider value={{ language, toggleLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
};

const useLanguage = () => {
  const context = React.useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within LanguageProvider');
  }
  return context;
};

// Student Context
const StudentContext = React.createContext();

const StudentProvider = ({ children }) => {
  const [student, setStudent] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const savedStudent = localStorage.getItem('eduquest_student');
    if (savedStudent) {
      try {
        setStudent(JSON.parse(savedStudent));
      } catch (e) {
        localStorage.removeItem('eduquest_student');
      }
    }
    setLoading(false);
  }, []);
  
  const saveStudent = (studentData) => {
    setStudent(studentData);
    localStorage.setItem('eduquest_student', JSON.stringify(studentData));
  };
  
  const clearStudent = () => {
    setStudent(null);
    localStorage.removeItem('eduquest_student');
  };
  
  return (
    <StudentContext.Provider value={{ student, saveStudent, clearStudent, loading }}>
      {children}
    </StudentContext.Provider>
  );
};

const useStudent = () => {
  const context = React.useContext(StudentContext);
  if (!context) {
    throw new Error('useStudent must be used within StudentProvider');
  }
  return context;
};

// Components
const LanguageToggle = () => {
  const { language, toggleLanguage } = useLanguage();
  
  return (
    <button
      onClick={toggleLanguage}
      className="fixed top-4 right-4 z-50 bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-full font-bold shadow-lg transition-all duration-200 transform hover:scale-105"
    >
      {language === 'english' ? 'ଓଡ଼ିଆ' : 'English'}
    </button>
  );
};

const HomePage = ({ onStartLearning }) => {
  const { language } = useLanguage();
  
  const content = {
    english: {
      title: "EduQuest Odisha",
      subtitle: "Adventure-Based Learning for Young Warriors",
      mission: "Join the quest to protect knowledge and discover the wonders of Odisha!",
      startButton: "Start Your Quest",
      features: [
        "🎮 Interactive Games & Stories",
        "🏆 Earn Badges & Rewards", 
        "🌟 Track Your Progress",
        "🛡️ Become a Knowledge Warrior"
      ]
    },
    odia: {
      title: "ଏଡୁକ୍ୱେଷ୍ଟ ଓଡ଼ିଶା",
      subtitle: "ତରୁଣ ଯୋଦ୍ଧାମାନଙ୍କ ପାଇଁ ଦୁଃସାହସିକ ଶିକ୍ଷା",
      mission: "ଜ୍ଞାନ ରକ୍ଷା କରିବା ଏବଂ ଓଡ଼ିଶାର ଆଶ୍ଚର୍ଯ୍ୟ ଆବିଷ୍କାର କରିବା ପାଇଁ ଅନ୍ୱେଷଣରେ ଯୋଗ ଦିଅ!",
      startButton: "ତୁମର ଅନ୍ୱେଷଣ ଆରମ୍ଭ କର",
      features: [
        "🎮 ଇଣ୍ଟରାକ୍ଟିଭ ଗେମ୍ସ ଏବଂ କାହାଣୀ",
        "🏆 ବ୍ୟାଜ୍ ଏବଂ ପୁରସ୍କାର ଅର୍ଜନ କର",
        "🌟 ତୁମର ପ୍ରଗତି ଟ୍ରାକ୍ କର",
        "🛡️ ଜ୍ଞାନ ଯୋଦ୍ଧା ହୁଅ"
      ]
    }
  };
  
  const currentContent = content[language];
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-400 via-purple-500 to-pink-500 relative overflow-hidden">
      {/* Enhanced Animated Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute top-20 left-10 w-20 h-20 bg-yellow-300 rounded-full opacity-70 animate-bounce"></div>
        <div className="absolute top-40 right-20 w-16 h-16 bg-green-300 rounded-full opacity-60 animate-pulse"></div>
        <div className="absolute bottom-20 left-1/4 w-12 h-12 bg-red-300 rounded-full opacity-50 animate-bounce delay-100"></div>
        <div className="absolute bottom-40 right-1/3 w-14 h-14 bg-blue-300 rounded-full opacity-60 animate-pulse delay-200"></div>
        
        {/* Floating Stars Animation */}
        <div className="absolute top-32 left-1/2 w-8 h-8 text-yellow-200 animate-spin">⭐</div>
        <div className="absolute top-60 right-1/4 w-6 h-6 text-white animate-bounce delay-300">✨</div>
        <div className="absolute bottom-32 left-1/3 w-10 h-10 text-yellow-300 animate-pulse delay-500">🌟</div>
        
        {/* Animated Clouds */}
        <div className="absolute top-16 left-0 w-24 h-12 bg-white bg-opacity-30 rounded-full animate-pulse"></div>
        <div className="absolute top-24 right-0 w-20 h-10 bg-white bg-opacity-20 rounded-full animate-pulse delay-200"></div>
      </div>
      
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen text-center px-6">
        {/* Enhanced Hero Section with Animation */}
        <div className="mb-8 transform hover:scale-105 transition-all duration-300">
          <div className="relative">
            <img 
              src="https://images.unsplash.com/photo-1650521552329-4a669b69b7b8" 
              alt="Warrior Mascot"
              className="w-32 h-32 mx-auto mb-6 rounded-full shadow-2xl animate-bounce hover:animate-spin transition-all duration-500"
            />
            {/* Magical glow effect */}
            <div className="absolute inset-0 w-32 h-32 mx-auto mb-6 rounded-full bg-yellow-300 opacity-20 animate-ping"></div>
          </div>
          
          <h1 className="text-6xl font-bold text-white mb-4 drop-shadow-lg animate-pulse">
            {currentContent.title}
          </h1>
          <p className="text-2xl text-yellow-200 mb-6 font-semibold animate-fadeIn">
            {currentContent.subtitle}
          </p>
          <p className="text-lg text-white mb-8 max-w-2xl mx-auto animate-slideInUp">
            {currentContent.mission}
          </p>
        </div>
        
        {/* Enhanced Features Grid with Hover Effects */}
        <div className="grid grid-cols-2 gap-4 mb-8 max-w-2xl">
          {currentContent.features.map((feature, index) => (
            <div key={index} 
                 className="bg-white bg-opacity-20 backdrop-blur rounded-lg p-4 text-white font-medium 
                           transform hover:scale-110 hover:bg-opacity-30 transition-all duration-300 
                           hover:shadow-xl cursor-pointer animate-slideInLeft"
                 style={{animationDelay: `${index * 0.2}s`}}>
              {feature}
            </div>
          ))}
        </div>
        
        {/* Village Background */}
        <div className="absolute bottom-0 left-0 right-0 h-40">
          <img 
            src="https://images.unsplash.com/photo-1629878006094-12bce6da1b63" 
            alt="Village Background"
            className="w-full h-full object-cover opacity-30"
          />
        </div>
        
        {/* Enhanced Start Button with Glow Effect */}
        <button
          onClick={onStartLearning}
          className="relative z-20 bg-green-500 hover:bg-green-600 text-white text-2xl font-bold py-4 px-8 rounded-full 
                     shadow-xl transform hover:scale-110 transition-all duration-300 animate-pulse hover:animate-none
                     hover:shadow-2xl hover:shadow-green-300/50"
        >
          <span className="relative z-10">{currentContent.startButton}</span>
          {/* Button glow effect */}
          <div className="absolute inset-0 bg-green-400 rounded-full opacity-50 animate-ping"></div>
        </button>
      </div>
      
      {/* CSS Animation Styles */}
      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        
        @keyframes slideInUp {
          from { 
            opacity: 0; 
            transform: translateY(30px); 
          }
          to { 
            opacity: 1; 
            transform: translateY(0); 
          }
        }
        
        @keyframes slideInLeft {
          from { 
            opacity: 0; 
            transform: translateX(-30px); 
          }
          to { 
            opacity: 1; 
            transform: translateX(0); 
          }
        }
        
        .animate-fadeIn {
          animation: fadeIn 1s ease-out;
        }
        
        .animate-slideInUp {
          animation: slideInUp 1s ease-out;
        }
        
        .animate-slideInLeft {
          animation: slideInLeft 1s ease-out;
        }
      `}</style>
    </div>
  );
};

const OnboardingPage = ({ onComplete }) => {
  const { language } = useLanguage();
  const [formData, setFormData] = useState({
    name: '',
    age: 6,
    grade: 1,
    avatar: 'boy'
  });
  
  const content = {
    english: {
      title: "Welcome, Young Warrior!",
      subtitle: "Let's create your adventure profile",
      nameLabel: "What's your name?",
      ageLabel: "How old are you?",
      gradeLabel: "Which class are you in?",
      avatarLabel: "Choose your avatar:",
      startButton: "Begin My Quest!"
    },
    odia: {
      title: "ସ୍ୱାଗତ, ତରୁଣ ଯୋଦ୍ଧା!",
      subtitle: "ଚାଲ ତୁମର ଦୁଃସାହସିକ ପ୍ରୋଫାଇଲ୍ ତିଆରି କରିବା",
      nameLabel: "ତୁମର ନାମ କଣ?",
      ageLabel: "ତୁମର ବୟସ କେତେ?",
      gradeLabel: "ତୁମେ କେଉଁ ଶ୍ରେଣୀରେ ପଢ଼?",
      avatarLabel: "ତୁମର ଅବତାର ବାଛ:",
      startButton: "ମୋର ଅନ୍ୱେଷଣ ଆରମ୍ଭ କର!"
    }  
  };
  
  const currentContent = content[language];
  
  const avatars = [
    { id: 'boy', emoji: '👦', name: 'Boy / ପୁଅ' },
    { id: 'girl', emoji: '👧', name: 'Girl / ଝିଅ' },
    { id: 'warrior', emoji: '🛡️', name: 'Warrior / ଯୋଦ୍ଧା' },
    { id: 'student', emoji: '📚', name: 'Student / ଛାତ୍ର' }
  ];
  
  const handleSubmit = async () => {
    try {
      const response = await axios.post(`${API}/students`, {
        ...formData,
        language: language
      });
      onComplete(response.data);
    } catch (error) {
      console.error('Error creating student:', error);
      alert('Error creating profile. Please try again.');
    }
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-400 to-blue-600 flex items-center justify-center px-6">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full">
        <div className="text-center mb-6">
          <h2 className="text-3xl font-bold text-gray-800 mb-2">{currentContent.title}</h2>
          <p className="text-gray-600">{currentContent.subtitle}</p>
        </div>
        
        <div className="space-y-6">
          {/* Name Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {currentContent.nameLabel}
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter your name"
            />
          </div>
          
          {/* Age Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {currentContent.ageLabel}
            </label>
            <select
              value={formData.age}
              onChange={(e) => setFormData({...formData, age: parseInt(e.target.value)})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {[5,6,7,8,9].map(age => (
                <option key={age} value={age}>{age}</option>
              ))}
            </select>
          </div>
          
          {/* Grade Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {currentContent.gradeLabel}
            </label>
            <select
              value={formData.grade}
              onChange={(e) => setFormData({...formData, grade: parseInt(e.target.value)})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value={1}>Class 1</option>
              <option value={2}>Class 2</option>
            </select>
          </div>
          
          {/* Avatar Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {currentContent.avatarLabel}
            </label>
            <div className="grid grid-cols-2 gap-3">
              {avatars.map(avatar => (
                <button
                  key={avatar.id}
                  onClick={() => setFormData({...formData, avatar: avatar.id})}
                  className={`p-3 rounded-lg border-2 transition-all duration-200 ${
                    formData.avatar === avatar.id 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="text-2xl mb-1">{avatar.emoji}</div>
                  <div className="text-xs text-gray-600">{avatar.name}</div>
                </button>
              ))}
            </div>
          </div>
          
          {/* Submit Button */}
          <button
            onClick={handleSubmit}
            disabled={!formData.name.trim()}
            className="w-full bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white font-bold py-3 px-4 rounded-lg transition-all duration-200 transform hover:scale-105 disabled:transform-none"
          >
            {currentContent.startButton}
          </button>
        </div>
      </div>
    </div>
  );
};

const StudentDashboard = () => {
  const { language } = useLanguage();
  const { student, saveStudent } = useStudent();
  const [quests, setQuests] = useState([]);
  const [progress, setProgress] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedQuest, setSelectedQuest] = useState(null);
  
  useEffect(() => {
    loadData();
  }, [student]);
  
  const loadData = async () => {
    try {
      const [questsRes, progressRes, studentRes] = await Promise.all([
        axios.get(`${API}/quests?grade=${student.grade}`),
        axios.get(`${API}/students/${student.id}/progress`),
        axios.get(`${API}/students/${student.id}`)
      ]);
      
      setQuests(questsRes.data);
      setProgress(progressRes.data);
      saveStudent(studentRes.data); // Update student data
      setLoading(false);
    } catch (error) {
      console.error('Error loading data:', error);
      setLoading(false);
    }
  };
  
  const content = {
    english: {
      welcome: `Welcome back, ${student?.name}!`,
      level: `Level ${student?.level || 1}`,
      xp: `${student?.total_xp || 0} XP`,
      streak: `${student?.current_streak || 0} day streak`,
      quests: "Available Quests",
      math: "Math Adventures",
      social: "Social Studies",
      play: "Play Quest",
      completed: "Completed"
    },
    odia: {
      welcome: `ପୁନଃ ସ୍ୱାଗତ, ${student?.name}!`,
      level: `ସ୍ତର ${student?.level || 1}`,
      xp: `${student?.total_xp || 0} XP`,
      streak: `${student?.current_streak || 0} ଦିନର ଧାରା`,
      quests: "ଉପଲବ୍ଧ ଅନ୍ୱେଷଣ",
      math: "ଗଣିତ ଦୁଃସାହସିକ",
      social: "ସାମାଜିକ ଅଧ୍ୟୟନ",
      play: "ଅନ୍ୱେଷଣ ଖେଳ",
      completed: "ସମ୍ପୂର୍ଣ୍ଣ"
    }
  };
  
  const currentContent = content[language];
  
  const getQuestProgress = (questId) => {
    return progress.find(p => p.quest_id === questId);
  };
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-400 to-pink-600 flex items-center justify-center">
        <div className="text-white text-2xl font-bold animate-pulse">Loading your quest...</div>
      </div>
    );
  }
  
  if (selectedQuest) {
    return <QuestPage quest={selectedQuest} onBack={() => setSelectedQuest(null)} onComplete={loadData} />;
  }
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-400 via-blue-500 to-green-500">
      {/* Header */}
      <div className="bg-white bg-opacity-20 backdrop-blur p-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-white">{currentContent.welcome}</h1>
            <div className="flex gap-4 mt-2 text-yellow-200">
              <span className="font-bold">{currentContent.level}</span>
              <span>{currentContent.xp}</span>
              <span>🔥 {currentContent.streak}</span>
            </div>
          </div>
          <div className="text-6xl">
            {student?.avatar === 'boy' ? '👦' : student?.avatar === 'girl' ? '👧' : student?.avatar === 'warrior' ? '🛡️' : '📚'}
          </div>
        </div>
        
        {/* XP Progress Bar */}
        <div className="mt-4">
          <div className="bg-white bg-opacity-30 rounded-full h-3 overflow-hidden">
            <div 
              className="bg-yellow-400 h-full transition-all duration-500"
              style={{ width: `${((student?.total_xp || 0) % 100)}%` }}
            ></div>
          </div>
        </div>
      </div>
      
      {/* Village Map / Quest Grid */}
      <div className="p-6">
        <h2 className="text-2xl font-bold text-white mb-6 text-center">{currentContent.quests}</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
          {quests.map((quest) => {
            const questProgress = getQuestProgress(quest.id);
            const isCompleted = questProgress?.completed;
            
            return (
              <div key={quest.id} className="bg-white rounded-2xl shadow-xl overflow-hidden transform hover:scale-105 transition-all duration-200">
                <div className={`h-2 ${quest.subject === 'math' ? 'bg-blue-500' : 'bg-green-500'}`}></div>
                
                <div className="p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-xl font-bold text-gray-800">
                        {language === 'english' ? quest.title : quest.title_odia}
                      </h3>
                      <p className="text-gray-600 text-sm mt-1">
                        {language === 'english' ? quest.description : quest.description_odia}
                      </p>
                    </div>
                    <div className="text-2xl">
                      {quest.subject === 'math' ? '🧮' : '🏛️'}
                    </div>
                  </div>
                  
                  <div className="flex justify-between items-center mb-4">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      quest.subject === 'math' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
                    }`}>
                      {quest.subject === 'math' ? currentContent.math : currentContent.social}
                    </span>
                    <span className="text-yellow-600 font-bold">+{quest.xp_reward} XP</span>
                  </div>
                  
                  {isCompleted && (
                    <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium mb-3 inline-block">
                      ✅ {currentContent.completed}
                    </div>
                  )}
                  
                  <button
                    onClick={() => setSelectedQuest(quest)}
                    className={`w-full py-3 px-4 rounded-lg font-bold transition-all duration-200 ${
                      isCompleted 
                        ? 'bg-gray-200 text-gray-600 hover:bg-gray-300' 
                        : 'bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:from-purple-600 hover:to-pink-600 transform hover:scale-105'
                    }`}
                  >
                    {currentContent.play}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

const QuestPage = ({ quest, onBack, onComplete }) => {
  const { language } = useLanguage();
  const { student } = useStudent();
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [showResult, setShowResult] = useState(false);
  const [result, setResult] = useState(null);
  const [hint, setHint] = useState('');
  const [showHint, setShowHint] = useState(false);
  
  const currentQuestion = quest.questions[currentQuestionIndex];
  const isLastQuestion = currentQuestionIndex === quest.questions.length - 1;
  
  const content = {
    english: {
      back: "← Back to Quests",
      question: `Question ${currentQuestionIndex + 1} of ${quest.questions.length}`,
      next: "Next Question",
      submit: "Submit Quest",
      hint: "Get Hint 💡",
      hideHint: "Hide Hint",
      excellent: "Excellent Work!",
      good: "Good Try!",
      completed: "Quest Completed!",
      retry: "Try Again",
      continue: "Continue Learning"
    },
    odia: {
      back: "← ଅନ୍ୱେଷଣକୁ ଫେରନ୍ତୁ",
      question: `ପ୍ରଶ୍ନ ${currentQuestionIndex + 1} ର ${quest.questions.length}`,
      next: "ପରବର୍ତ୍ତୀ ପ୍ରଶ୍ନ",
      submit: "ଅନ୍ୱେଷଣ ଦାଖଲ କରନ୍ତୁ",
      hint: "ସୂଚନା ପାଆନ୍ତୁ 💡",
      hideHint: "ସୂଚନା ଲୁଚାନ୍ତୁ",
      excellent: "ଉତ୍କୃଷ୍ଟ କାମ!",
      good: "ଭଲ ଚେଷ୍ଟା!",
      completed: "ଅନ୍ୱେଷଣ ସମ୍ପୂର୍ଣ୍ଣ!",
      retry: "ପୁନଃ ଚେଷ୍ଟା କରନ୍ତୁ",
      continue: "ଶିଖିବା ଜାରି ରଖନ୍ତୁ"
    }
  };
  
  const currentContent = content[language];
  
  const handleAnswer = (answer) => {
    setAnswers({
      ...answers,
      [currentQuestion.id]: answer
    });
  };
  
  const handleNext = () => {
    if (isLastQuestion) {
      submitQuest();
    } else {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setShowHint(false);
      setHint('');
    }
  };
  
  const submitQuest = async () => {
    try {
      const submission = {
        quest_id: quest.id,
        answers: Object.entries(answers).map(([question_id, answer]) => ({
          question_id,
          answer
        }))
      };
      
      const response = await axios.post(`${API}/students/${student.id}/submit_quest`, submission);
      setResult(response.data);
      setShowResult(true);
    } catch (error) {
      console.error('Error submitting quest:', error);
      alert('Error submitting quest. Please try again.');
    }
  };
  
  const getHint = async () => {
    if (showHint) {
      setShowHint(false);
      return;
    }
    
    try {
      const response = await axios.post(`${API}/students/${student.id}/generate_hint?quest_id=${quest.id}&question_id=${currentQuestion.id}`);
      setHint(language === 'english' ? response.data.hint : response.data.hint_odia);
      setShowHint(true);
    } catch (error) {
      console.error('Error getting hint:', error);
      setHint(language === 'english' ? 
        'Take your time and think step by step!' : 
        'ତୁମର ସମୟ ନିଅ ଏବଂ ଧାପେ ଧାପେ ଚିନ୍ତା କର!');
      setShowHint(true);
    }
  };
  
  if (showResult) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-400 to-blue-600 flex items-center justify-center px-6">
        <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full text-center">
          <div className="text-6xl mb-4">
            {result.completed ? '🎉' : '💪'}
          </div>
          <h2 className="text-3xl font-bold text-gray-800 mb-4">
            {result.completed ? currentContent.excellent : currentContent.good}
          </h2>
          <div className="space-y-2 mb-6">
            <p className="text-lg">Score: {result.score}%</p>
            <p className="text-lg">XP Earned: +{result.xp_earned}</p>
            <p className="text-lg">Correct: {result.correct_answers}/{result.total_questions}</p>
            {result.new_badges.length > 0 && (
              <div className="bg-yellow-100 p-3 rounded-lg">
                <p className="font-bold text-yellow-800">New Badges! 🏆</p>
                {result.new_badges.map(badge => (
                  <p key={badge} className="text-yellow-700">{badge}</p>
                ))}
              </div>
            )}
          </div>
          <button
            onClick={() => {
              onComplete();
              onBack();
            }}
            className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-4 rounded-lg transition-all duration-200"
          >
            {currentContent.continue}
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-400 via-purple-500 to-pink-500">
      {/* Header */}
      <div className="bg-white bg-opacity-20 backdrop-blur p-6">
        <button
          onClick={onBack}
          className="text-white hover:text-yellow-200 font-bold mb-4"
        >
          {currentContent.back}
        </button>
        <h1 className="text-3xl font-bold text-white mb-2">
          {language === 'english' ? quest.title : quest.title_odia}
        </h1>
        <p className="text-yellow-200">
          {language === 'english' ? quest.story_context : quest.story_context_odia}
        </p>
        <div className="mt-4 text-white font-bold">
          {currentContent.question}
        </div>
      </div>
      
      {/* Question */}
      <div className="p-6 flex-1 flex items-center justify-center">
        <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-2xl w-full">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">
            {language === 'english' ? currentQuestion.question : currentQuestion.question_odia}
          </h2>
          
          {/* Question Image */}
          {currentQuestion.image_url && (
            <img 
              src={currentQuestion.image_url} 
              alt="Question" 
              className="w-full h-48 object-cover rounded-lg mb-6"
            />
          )}
          
          {/* Answer Options */}
          <div className="space-y-3 mb-6">
            {currentQuestion.options.map((option, index) => (
              <button
                key={index}
                onClick={() => handleAnswer(option)}
                className={`w-full p-4 text-left rounded-lg border-2 transition-all duration-200 ${
                  answers[currentQuestion.id] === option
                    ? 'border-blue-500 bg-blue-50 text-blue-800'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <span className="font-bold mr-3">{String.fromCharCode(65 + index)}.</span>
                {option}
              </button>
            ))}
          </div>
          
          {/* Hint Section */}
          <div className="mb-6">
            <button
              onClick={getHint}
              className="text-purple-600 hover:text-purple-800 font-bold flex items-center gap-2"
            >
              {showHint ? currentContent.hideHint : currentContent.hint}
            </button>
            {showHint && hint && (
              <div className="mt-3 p-4 bg-yellow-50 border-l-4 border-yellow-400 rounded">
                <p className="text-yellow-800">{hint}</p>
              </div>
            )}
          </div>
          
          {/* Navigation */}
          <button
            onClick={handleNext}
            disabled={!answers[currentQuestion.id]}
            className="w-full bg-purple-500 hover:bg-purple-600 disabled:bg-gray-300 text-white font-bold py-3 px-4 rounded-lg transition-all duration-200 transform hover:scale-105 disabled:transform-none"
          >
            {isLastQuestion ? currentContent.submit : currentContent.next}
          </button>
        </div>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  const [currentView, setCurrentView] = useState('home'); // 'home', 'onboarding', 'dashboard'
  
  return (
    <LanguageProvider>
      <StudentProvider>
        <AppContent currentView={currentView} setCurrentView={setCurrentView} />
      </StudentProvider>
    </LanguageProvider>
  );
}

function AppContent({ currentView, setCurrentView }) {
  const { student, loading, saveStudent } = useStudent();
  
  useEffect(() => {
    if (!loading) {
      if (student) {
        setCurrentView('dashboard');
      } else {
        setCurrentView('home');
      }
    }
  }, [student, loading, setCurrentView]);
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-400 to-purple-600 flex items-center justify-center">
        <div className="text-white text-2xl font-bold animate-pulse">Loading EduQuest Odisha...</div>
      </div>
    );
  }
  
  return (
    <div className="App">
      <LanguageToggle />
      
      {currentView === 'home' && (
        <HomePage onStartLearning={() => setCurrentView('onboarding')} />
      )}
      
      {currentView === 'onboarding' && (
        <OnboardingPage onComplete={(studentData) => {
          setCurrentView('dashboard');
        }} />
      )}
      
      {currentView === 'dashboard' && student && (
        <StudentDashboard />
      )}
    </div>
  );
}

export default App;