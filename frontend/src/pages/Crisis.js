import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { ArrowLeft, Phone, Mail, LifeBuoy, AlertTriangle } from 'lucide-react';

export default function Crisis() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background bg-noise">
      <header className="border-b border-border/40 bg-card/50 backdrop-blur-xl">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <Button
            data-testid="back-btn"
            onClick={() => navigate('/dashboard')}
            variant="ghost"
            className="hover:bg-muted/50 rounded-full"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back
          </Button>
        </div>
      </header>

      <div data-testid="crisis-resources-page" className="max-w-4xl mx-auto px-6 py-16">
        <div className="bg-secondary/10 border-2 border-secondary/30 rounded-2xl p-8 mb-8">
          <div className="flex items-start gap-4 mb-4">
            <AlertTriangle className="w-8 h-8 text-secondary flex-shrink-0" />
            <div>
              <h1 className="font-fraunces text-3xl font-medium mb-2">Crisis Support Resources</h1>
              <p className="text-lg text-muted-foreground">
                If you're experiencing a mental health crisis, please reach out for immediate professional support.
              </p>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          {/* National Crisis Hotline */}
          <div className="bg-card rounded-2xl shadow-soft border border-border/40 p-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                <Phone className="w-6 h-6 text-primary" />
              </div>
              <div>
                <h2 className="font-fraunces text-2xl font-medium">National Crisis Hotline</h2>
                <p className="text-muted-foreground">24/7 Support</p>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between p-4 bg-muted/20 rounded-xl">
                <span className="font-medium">Call or Text:</span>
                <a href="tel:988" className="text-2xl font-bold text-primary hover:underline">988</a>
              </div>
              <p className="text-sm text-muted-foreground px-4">
                The 988 Suicide & Crisis Lifeline provides free and confidential support for people in distress.
              </p>
            </div>
          </div>

          {/* Emergency Services */}
          <div className="bg-card rounded-2xl shadow-soft border border-border/40 p-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-full bg-secondary/10 flex items-center justify-center">
                <LifeBuoy className="w-6 h-6 text-secondary" />
              </div>
              <div>
                <h2 className="font-fraunces text-2xl font-medium">Emergency Services</h2>
                <p className="text-muted-foreground">Immediate Danger</p>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between p-4 bg-muted/20 rounded-xl">
                <span className="font-medium">Emergency:</span>
                <a href="tel:911" className="text-2xl font-bold text-secondary hover:underline">911</a>
              </div>
              <p className="text-sm text-muted-foreground px-4">
                If you or someone else is in immediate danger, call 911 or go to the nearest emergency room.
              </p>
            </div>
          </div>

          {/* Campus Resources */}
          <div className="bg-card rounded-2xl shadow-soft border border-border/40 p-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-full bg-accent/10 flex items-center justify-center">
                <Mail className="w-6 h-6 text-accent" />
              </div>
              <div>
                <h2 className="font-fraunces text-2xl font-medium">Campus Counseling Center</h2>
                <p className="text-muted-foreground">Student Support Services</p>
              </div>
            </div>
            <div className="space-y-3 px-4">
              <p className="text-muted-foreground">
                Your campus counseling center offers professional mental health support specifically for students.
              </p>
              <div className="space-y-2">
                <div className="p-3 bg-muted/20 rounded-lg">
                  <p className="text-sm font-medium mb-1">Find Your Campus Resources:</p>
                  <p className="text-sm text-muted-foreground">
                    Contact your student health center or visit your university's counseling services website.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Additional Resources */}
          <div className="bg-card rounded-2xl shadow-soft border border-border/40 p-8">
            <h2 className="font-fraunces text-2xl font-medium mb-4">Additional Resources</h2>
            <div className="space-y-3">
              <div className="p-4 border border-border/40 rounded-xl">
                <h3 className="font-medium mb-1">Crisis Text Line</h3>
                <p className="text-sm text-muted-foreground mb-2">
                  Text HOME to <span className="font-bold">741741</span> to connect with a Crisis Counselor
                </p>
              </div>
              <div className="p-4 border border-border/40 rounded-xl">
                <h3 className="font-medium mb-1">SAMHSA National Helpline</h3>
                <p className="text-sm text-muted-foreground mb-2">
                  Call <span className="font-bold">1-800-662-4357</span> for free, confidential, 24/7 support
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8 bg-muted/30 rounded-xl p-6">
          <p className="text-sm text-muted-foreground text-center">
            Remember: Reaching out for help is a sign of strength, not weakness. You don't have to face this alone.
          </p>
        </div>
      </div>
    </div>
  );
}