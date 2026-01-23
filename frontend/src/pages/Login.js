import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { login } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { toast } from 'sonner';
import axios from 'axios';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function Login() {
  const navigate = useNavigate();
  const { loginUser } = useAuth();
  const [loading, setLoading] = useState(false);
  const [showOTP, setShowOTP] = useState(false);
  const [otpData, setOtpData] = useState(null);
  const [otp, setOtp] = useState('');
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await login(formData.email, formData.password);
      if (response.data.requires_otp) {
        setOtpData({
          user: response.data.user,
          temp_token: response.data.temp_token
        });
        setShowOTP(true);
        
        // Display OTP for testing
        if (response.data.otp_code_test) {
          toast.success(`Testing Mode: Your OTP is ${response.data.otp_code_test}`, { duration: 10000 });
        } else {
          toast.success('OTP sent to your email and phone!');
        }
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/auth/verify-login-otp`, null, {
        params: {
          user_id: otpData.user.id,
          otp_code: otp,
          temp_token: otpData.temp_token
        }
      });
      loginUser(response.data.user, response.data.access_token);
      toast.success('Welcome back!');
      
      // Navigate based on role
      if (response.data.user.role === 'counselor') {
        navigate('/admin');
      } else {
        navigate('/dashboard');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Invalid OTP');
    } finally {
      setLoading(false);
    }
  };

  if (showOTP) {
    return (
      <div className="min-h-screen bg-background bg-noise flex items-center justify-center px-6">
        <div className="w-full max-w-md">
          <div className="bg-card rounded-2xl shadow-float p-8 border border-border/40">
            <h1 className="font-fraunces text-4xl font-normal mb-2 text-center">Verify OTP</h1>
            <p className="text-muted-foreground text-center mb-8">
              Enter the 6-digit code sent to your email and phone
            </p>

            <form onSubmit={handleVerifyOTP} className="space-y-6">
              <div>
                <Input
                  data-testid="otp-input"
                  type="text"
                  maxLength={6}
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                  required
                  className="w-full bg-white/50 border-border/60 focus:border-primary/50 focus:ring-4 focus:ring-primary/5 rounded-xl h-16 px-4 text-center text-3xl tracking-widest"
                  placeholder="000000"
                />
              </div>

              <Button
                data-testid="verify-otp-btn"
                type="submit"
                disabled={loading || otp.length !== 6}
                className="w-full bg-primary text-primary-foreground hover:bg-primary/90 rounded-full py-6 text-lg font-medium shadow-soft hover:shadow-float transition-all disabled:opacity-50"
              >
                {loading ? 'Verifying...' : 'Verify & Login'}
              </Button>
            </form>

            <p className="text-center text-sm text-muted-foreground mt-4">
              Didn't receive the code? Check your spam folder.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background bg-noise flex items-center justify-center px-6">
      <div className="w-full max-w-md">
        <div className="bg-card rounded-2xl shadow-float p-8 border border-border/40">
          <h1 className="font-fraunces text-4xl font-normal mb-2 text-center">Welcome Back</h1>
          <p className="text-muted-foreground text-center mb-8">Continue your wellness journey</p>

          <form data-testid="login-form" onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium mb-2">Email</label>
              <Input
                data-testid="email-input"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
                className="w-full bg-white/50 border-border/60 focus:border-primary/50 focus:ring-4 focus:ring-primary/5 rounded-xl h-12 px-4"
                placeholder="your@email.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Password</label>
              <Input
                data-testid="password-input"
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                required
                className="w-full bg-white/50 border-border/60 focus:border-primary/50 focus:ring-4 focus:ring-primary/5 rounded-xl h-12 px-4"
                placeholder="Enter your password"
              />
            </div>

            <Button
              data-testid="login-submit-btn"
              type="submit"
              disabled={loading}
              className="w-full bg-primary text-primary-foreground hover:bg-primary/90 rounded-full py-6 text-lg font-medium shadow-soft hover:shadow-float transition-all"
            >
              {loading ? 'Signing In...' : 'Continue'}
            </Button>
          </form>

          <div className="text-center mt-4">
            <Link to="/forgot-password" className="text-sm text-primary hover:underline">
              Forgot password?
            </Link>
          </div>

          <p className="text-center text-muted-foreground mt-6">
            Don't have an account?{' '}
            <Link to="/register" className="text-primary hover:underline">
              Register now
            </Link>
          </p>
        </div>

        <div className="mt-4 bg-muted/30 rounded-xl p-4 border border-border/40">
          <p className="text-xs text-muted-foreground text-center">
            🔒 Secure 2-Factor Authentication: You'll receive a 6-digit OTP on your email and phone
          </p>
        </div>
      </div>
    </div>
  );
}