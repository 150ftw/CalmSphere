import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { login } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { toast } from 'sonner';

export default function Login() {
  const navigate = useNavigate();
  const { loginUser } = useAuth();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await login(formData.email, formData.password);
      loginUser(response.data.user, response.data.access_token);
      toast.success('Welcome back!');
      
      // Navigate based on role
      if (response.data.user.role === 'counselor') {
        navigate('/admin');
      } else {
        navigate('/dashboard');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

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
              {loading ? 'Signing In...' : 'Sign In'}
            </Button>
          </form>

          <p className="text-center text-muted-foreground mt-6">
            Don't have an account?{' '}
            <Link to="/register" className="text-primary hover:underline">
              Register now
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}