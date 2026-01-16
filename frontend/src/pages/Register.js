import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { register } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Checkbox } from '../components/ui/checkbox';
import { toast } from 'sonner';

export default function Register() {
  const navigate = useNavigate();
  const { loginUser } = useAuth();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    username: '',
    is_pseudonymous: false,
    role: 'student'
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await register(formData);
      loginUser(response.data.user, response.data.access_token);
      toast.success('Welcome to CalmSphere AI!');
      navigate('/onboarding');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background bg-noise flex items-center justify-center px-6">
      <div className="w-full max-w-md">
        <div className="bg-card rounded-2xl shadow-float p-8 border border-border/40">
          <h1 className="font-fraunces text-4xl font-normal mb-2 text-center">Join CalmSphere</h1>
          <p className="text-muted-foreground text-center mb-8">Start your mental wellness journey</p>

          <form data-testid="register-form" onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium mb-2">Username</label>
              <Input
                data-testid="username-input"
                type="text"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                required
                className="w-full bg-white/50 border-border/60 focus:border-primary/50 focus:ring-4 focus:ring-primary/5 rounded-xl h-12 px-4"
                placeholder="Enter your username"
              />
            </div>

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
                placeholder="Create a password"
              />
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                data-testid="pseudonymous-checkbox"
                checked={formData.is_pseudonymous}
                onCheckedChange={(checked) => setFormData({ ...formData, is_pseudonymous: checked })}
                id="pseudonymous"
              />
              <label htmlFor="pseudonymous" className="text-sm text-muted-foreground">
                Use pseudonymous account (enhanced privacy)
              </label>
            </div>

            <Button
              data-testid="register-submit-btn"
              type="submit"
              disabled={loading}
              className="w-full bg-primary text-primary-foreground hover:bg-primary/90 rounded-full py-6 text-lg font-medium shadow-soft hover:shadow-float transition-all"
            >
              {loading ? 'Creating Account...' : 'Create Account'}
            </Button>
          </form>

          <p className="text-center text-muted-foreground mt-6">
            Already have an account?{' '}
            <Link to="/login" className="text-primary hover:underline">
              Sign in
            </Link>
          </p>
        </div>

        <div className="mt-6 bg-muted/30 rounded-xl p-4 border border-border/40">
          <p className="text-sm text-muted-foreground text-center">
            By registering, you acknowledge that CalmSphere AI is a support tool and not a substitute for professional mental health care. In crisis, contact KIRAN: 1800-599-0019.
          </p>
        </div>
      </div>
    </div>
  );
}