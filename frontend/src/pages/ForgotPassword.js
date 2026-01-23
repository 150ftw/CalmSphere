import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function ForgotPassword() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1); // 1: email, 2: otp, 3: new password
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [resetData, setResetData] = useState(null);

  const handleRequestReset = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/auth/forgot-password`, null, {
        params: { email }
      });
      setResetData({
        user_id: response.data.user_id,
        temp_token: response.data.temp_token
      });
      setStep(2);
      
      // Display OTP for testing
      if (response.data.otp_code_test) {
        toast.success(`Testing Mode: Your OTP is ${response.data.otp_code_test}`, { duration: 10000 });
      } else {
        toast.success('OTP sent to your email and phone!');
      }
    } catch (error) {
      toast.error('Failed to send reset code');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    if (otp.length !== 6) {
      toast.error('Please enter a valid 6-digit OTP');
      return;
    }
    setStep(3);
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    
    if (newPassword.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }
    
    if (newPassword !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      await axios.post(`${API_URL}/auth/reset-password`, null, {
        params: {
          user_id: resetData.user_id,
          otp_code: otp,
          new_password: newPassword,
          temp_token: resetData.temp_token
        }
      });
      toast.success('Password reset successfully!');
      navigate('/login');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to reset password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background bg-noise flex items-center justify-center px-6">
      <div className="w-full max-w-md">
        <div className="mb-6">
          <Button
            onClick={() => navigate('/login')}
            variant="ghost"
            className="hover:bg-muted/50 rounded-full"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back to Login
          </Button>
        </div>

        <div className="bg-card rounded-2xl shadow-float p-8 border border-border/40">
          <h1 className="font-fraunces text-4xl font-normal mb-2 text-center">Reset Password</h1>
          
          {step === 1 && (
            <>
              <p className="text-muted-foreground text-center mb-8">
                Enter your email to receive a password reset code
              </p>

              <form data-testid="forgot-password-form" onSubmit={handleRequestReset} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium mb-2">Email Address</label>
                  <Input
                    data-testid="email-input"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full bg-white/50 border-border/60 focus:border-primary/50 focus:ring-4 focus:ring-primary/5 rounded-xl h-12 px-4"
                    placeholder="your@email.com"
                  />
                </div>

                <Button
                  data-testid="send-code-btn"
                  type="submit"
                  disabled={loading}
                  className="w-full bg-primary text-primary-foreground hover:bg-primary/90 rounded-full py-6 text-lg font-medium shadow-soft hover:shadow-float transition-all"
                >
                  {loading ? 'Sending...' : 'Send Reset Code'}
                </Button>
              </form>
            </>
          )}

          {step === 2 && (
            <>
              <p className="text-muted-foreground text-center mb-8">
                Enter the 6-digit code sent to your email and phone
              </p>

              <form data-testid="verify-otp-form" onSubmit={handleVerifyOTP} className="space-y-6">
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
                  data-testid="verify-code-btn"
                  type="submit"
                  disabled={otp.length !== 6}
                  className="w-full bg-primary text-primary-foreground hover:bg-primary/90 rounded-full py-6 text-lg font-medium shadow-soft hover:shadow-float transition-all disabled:opacity-50"
                >
                  Verify Code
                </Button>
              </form>

              <p className="text-center text-sm text-muted-foreground mt-4">
                Didn't receive the code?{' '}
                <button onClick={() => setStep(1)} className="text-primary hover:underline">
                  Try again
                </button>
              </p>
            </>
          )}

          {step === 3 && (
            <>
              <p className="text-muted-foreground text-center mb-8">
                Create a new password for your account
              </p>

              <form data-testid="reset-password-form" onSubmit={handleResetPassword} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium mb-2">New Password</label>
                  <Input
                    data-testid="new-password-input"
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    required
                    minLength={8}
                    className="w-full bg-white/50 border-border/60 focus:border-primary/50 focus:ring-4 focus:ring-primary/5 rounded-xl h-12 px-4"
                    placeholder="Enter new password (min 8 characters)"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Confirm Password</label>
                  <Input
                    data-testid="confirm-password-input"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    className="w-full bg-white/50 border-border/60 focus:border-primary/50 focus:ring-4 focus:ring-primary/5 rounded-xl h-12 px-4"
                    placeholder="Confirm new password"
                  />
                </div>

                <Button
                  data-testid="reset-password-btn"
                  type="submit"
                  disabled={loading}
                  className="w-full bg-primary text-primary-foreground hover:bg-primary/90 rounded-full py-6 text-lg font-medium shadow-soft hover:shadow-float transition-all"
                >
                  {loading ? 'Resetting...' : 'Reset Password'}
                </Button>
              </form>
            </>
          )}
        </div>

        <div className="mt-6 bg-muted/30 rounded-xl p-4 border border-border/40">
          <p className="text-xs text-muted-foreground text-center">
            {step === 1 && "We'll send a 6-digit verification code to your registered email and phone number"}
            {step === 2 && "The code is valid for 10 minutes"}
            {step === 3 && "Choose a strong password with at least 8 characters"}
          </p>
        </div>
      </div>
    </div>
  );
}
