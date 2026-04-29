import { Link } from 'react-router-dom';
import { 
  Camera, 
  Users, 
  BarChart3, 
  Shield, 
  Zap, 
  Clock,
  ChevronDown,
  Menu,
  X
} from 'lucide-react';
import { useState } from 'react';

export default function Landing() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  const features = [
    {
      icon: Camera,
      title: 'AI-Powered Recognition',
      description: 'Advanced facial recognition technology for accurate student identification'
    },
    {
      icon: Clock,
      title: 'Real-Time Tracking',
      description: 'Monitor attendance instantly with live camera integration'
    },
    {
      icon: Users,
      title: 'Student Management',
      description: 'Comprehensive student database with easy enrollment and management'
    },
    {
      icon: BarChart3,
      title: 'Analytics & Reports',
      description: 'Detailed insights and exportable reports for better decision making'
    },
    {
      icon: Shield,
      title: 'Secure & Private',
      description: 'Enterprise-grade security to protect sensitive student data'
    },
    {
      icon: Zap,
      title: 'Lightning Fast',
      description: 'Optimized performance for seamless attendance tracking'
    }
  ];

  const faqs = [
    {
      question: 'How does the facial recognition work?',
      answer: 'Our system uses advanced AI algorithms to detect and recognize faces in real-time. Simply register students with their photos, and the system will automatically identify them during attendance sessions.'
    },
    {
      question: 'Is the system accurate?',
      answer: 'Yes! Our facial recognition technology achieves over 99% accuracy in optimal conditions. The system continuously learns and improves with each use.'
    },
    {
      question: 'Can I export attendance reports?',
      answer: 'Absolutely! You can export attendance data in multiple formats including CSV, Excel, and PDF. Generate custom reports for any date range or class.'
    },
    {
      question: 'How many students can the system handle?',
      answer: 'The system is designed to scale. Whether you have 50 or 5000 students, our platform handles it efficiently without compromising performance.'
    },
    {
      question: 'What equipment do I need?',
      answer: 'All you need is a computer with a webcam or an external camera. The system works with standard USB cameras and built-in laptop cameras.'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Navbar */}
      <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md shadow-sm z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <Camera className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                SmartAttend
              </span>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <a href="#home" className="text-gray-700 hover:text-blue-600 transition-colors font-medium">
                Home
              </a>
              <a href="#about" className="text-gray-700 hover:text-blue-600 transition-colors font-medium">
                About
              </a>
              <a href="#features" className="text-gray-700 hover:text-blue-600 transition-colors font-medium">
                Features
              </a>
              <a href="#faq" className="text-gray-700 hover:text-blue-600 transition-colors font-medium">
                FAQ
              </a>
            </div>

            {/* Auth Buttons */}
            <div className="hidden md:flex items-center space-x-4">
              <Link 
                to="/login" 
                className="px-4 py-2 text-gray-700 hover:text-blue-600 transition-colors font-medium"
              >
                Login
              </Link>
              <Link 
                to="/signup" 
                className="px-6 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:shadow-lg hover:scale-105 transition-all duration-200 font-medium"
              >
                Sign Up
              </Link>
            </div>

            {/* Mobile Menu Button */}
            <button 
              className="md:hidden p-2"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t">
            <div className="px-4 py-4 space-y-3">
              <a href="#home" className="block text-gray-700 hover:text-blue-600 transition-colors font-medium">
                Home
              </a>
              <a href="#about" className="block text-gray-700 hover:text-blue-600 transition-colors font-medium">
                About
              </a>
              <a href="#features" className="block text-gray-700 hover:text-blue-600 transition-colors font-medium">
                Features
              </a>
              <a href="#faq" className="block text-gray-700 hover:text-blue-600 transition-colors font-medium">
                FAQ
              </a>
              <div className="pt-4 space-y-2">
                <Link 
                  to="/login" 
                  className="block w-full px-4 py-2 text-center text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium"
                >
                  Login
                </Link>
                <Link 
                  to="/signup" 
                  className="block w-full px-4 py-2 text-center bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:shadow-lg transition-all font-medium"
                >
                  Sign Up
                </Link>
              </div>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section id="home" className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold text-gray-900 mb-6 leading-tight">
              Smart Attendance
              <span className="block bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                Made Simple
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Transform your classroom with AI-powered facial recognition. 
              Track attendance effortlessly and focus on what matters most - teaching.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link 
                to="/signup" 
                className="px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:shadow-2xl hover:scale-105 transition-all duration-200 font-semibold text-lg"
              >
                Get Started Free
              </Link>
              <a 
                href="#features" 
                className="px-8 py-4 bg-white text-gray-700 rounded-xl hover:shadow-lg transition-all duration-200 font-semibold text-lg border border-gray-200"
              >
                Learn More
              </a>
            </div>
          </div>

          {/* Hero Image/Illustration */}
          <div className="mt-16 relative">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-indigo-400 rounded-3xl blur-3xl opacity-20"></div>
            <div className="relative bg-white rounded-3xl shadow-2xl p-8 border border-gray-100">
              <div className="aspect-video bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl flex items-center justify-center">
                <Camera className="w-32 h-32 text-blue-600 opacity-50" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              About SmartAttend
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Revolutionizing attendance management with cutting-edge AI technology
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h3 className="text-3xl font-bold text-gray-900 mb-6">
                Why Choose SmartAttend?
              </h3>
              <p className="text-lg text-gray-600 mb-6">
                SmartAttend is an innovative attendance management system that leverages 
                artificial intelligence and facial recognition to automate the attendance 
                tracking process. Say goodbye to manual roll calls and paper registers.
              </p>
              <p className="text-lg text-gray-600 mb-6">
                Our platform is designed for educational institutions of all sizes, 
                from small classrooms to large universities. With real-time tracking, 
                comprehensive analytics, and seamless integration, managing attendance 
                has never been easier.
              </p>
              <div className="flex flex-wrap gap-4">
                <div className="flex items-center space-x-2">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Shield className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900">Secure</p>
                    <p className="text-sm text-gray-600">Data Protection</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center">
                    <Zap className="w-6 h-6 text-indigo-600" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900">Fast</p>
                    <p className="text-sm text-gray-600">Real-time Processing</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-indigo-400 rounded-3xl blur-2xl opacity-20"></div>
              <div className="relative bg-gradient-to-br from-blue-50 to-indigo-50 rounded-3xl p-12 border border-gray-100">
                <Users className="w-full h-64 text-blue-600 opacity-30" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Powerful Features
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Everything you need to manage attendance efficiently and effectively
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div 
                key={index}
                className="group bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 border border-gray-100"
              >
                <div className="w-14 h-14 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <feature.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Frequently Asked Questions
            </h2>
            <p className="text-xl text-gray-600">
              Got questions? We've got answers
            </p>
          </div>

          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <div 
                key={index}
                className="bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow"
              >
                <button
                  className="w-full px-6 py-5 flex justify-between items-center text-left"
                  onClick={() => setOpenFaq(openFaq === index ? null : index)}
                >
                  <span className="text-lg font-semibold text-gray-900">
                    {faq.question}
                  </span>
                  <ChevronDown 
                    className={`w-5 h-5 text-gray-500 transition-transform ${
                      openFaq === index ? 'rotate-180' : ''
                    }`}
                  />
                </button>
                {openFaq === index && (
                  <div className="px-6 pb-5">
                    <p className="text-gray-600">
                      {faq.answer}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-5xl mx-auto">
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-3xl p-12 text-center shadow-2xl">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Ready to Get Started?
            </h2>
            <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
              Join hundreds of institutions already using SmartAttend to streamline their attendance management
            </p>
            <Link 
              to="/signup" 
              className="inline-block px-8 py-4 bg-white text-blue-600 rounded-xl hover:shadow-2xl hover:scale-105 transition-all duration-200 font-semibold text-lg"
            >
              Start Free Trial
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                  <Camera className="w-5 h-5 text-white" />
                </div>
                <span className="text-lg font-bold text-white">SmartAttend</span>
              </div>
              <p className="text-sm text-gray-400">
                AI-powered attendance management for modern education
              </p>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#features" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="#about" className="hover:text-white transition-colors">About</a></li>
                <li><a href="#faq" className="hover:text-white transition-colors">FAQ</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white transition-colors">About Us</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white transition-colors">Help Center</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Documentation</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Terms of Service</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 pt-8 text-center text-sm text-gray-400">
            <p>&copy; {new Date().getFullYear()} SmartAttend. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
