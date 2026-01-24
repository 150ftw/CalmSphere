# CalmSphere AI - Production OTP Setup Guide

## Overview
This guide will help you set up production-ready OTP (One-Time Password) authentication using:
- **SendGrid** for email OTPs
- **MSG91** (recommended for India) OR **Twilio** for SMS OTPs

---

## 🚀 Quick Start

### Step 1: Get API Keys

#### **SendGrid (Email Service)**

1. Go to [SendGrid](https://sendgrid.com/)
2. Sign up for a free account (100 emails/day free forever)
3. Verify your email address
4. Navigate to: **Settings** → **API Keys**
5. Click **Create API Key**
6. Name it "CalmSphere Production"
7. Select **Full Access** permissions
8. Copy the API key (you'll only see it once!)

**Verify Sender Email:**
- Go to **Settings** → **Sender Authentication**
- Click **Verify a Single Sender**
- Add your email (e.g., noreply@yourdomain.com)
- Verify via the email you receive

#### **MSG91 (SMS Service - Recommended for India)**

1. Go to [MSG91](https://msg91.com/)
2. Sign up and verify your account
3. Get ₹20 free credits on signup
4. Navigate to **API** section
5. Copy your **Auth Key**

**Create SMS Template:**
6. Go to **Manage** → **Templates**
7. Click **Create Template**
8. Template Type: **OTP**
9. Template content:
   ```
   Your CalmSphere AI OTP is {OTP}. Valid for 10 minutes. Never share this code.
   ```
10. Submit for approval (usually approved within hours)
11. Copy the **Template ID** once approved

**Pricing:** ₹0.15 - ₹0.20 per SMS in India

#### **Alternative: Twilio (SMS Service - International)**

1. Go to [Twilio](https://www.twilio.com/)
2. Sign up for free ($15 trial credit)
3. Verify your phone number
4. Dashboard → Get a **Trial Phone Number**
5. Copy:
   - **Account SID**
   - **Auth Token** (click to reveal)
   - **Phone Number** (with country code)

**Pricing:** $0.0079 per SMS in India

---

### Step 2: Configure Environment Variables

Edit `/app/backend/.env` file:

```bash
# Email Configuration (SendGrid)
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=noreply@yourdomain.com

# SMS Configuration - CHOOSE ONE:

# Option 1: MSG91 (Recommended for India)
MSG91_AUTH_KEY=your_actual_auth_key_here
MSG91_TEMPLATE_ID=your_template_id_here
MSG91_SENDER_ID=CLMSPH
USE_MSG91=true

# Option 2: Twilio (Alternative)
# TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# TWILIO_AUTH_TOKEN=your_auth_token_here
# TWILIO_PHONE_NUMBER=+1234567890
# USE_MSG91=false

# OTP Configuration
ENABLE_OTP_TESTING_MODE=false  # Set to 'true' for development, 'false' for production
```

---

### Step 3: Restart Backend

```bash
sudo supervisorctl restart backend
```

---

## 🧪 Testing Mode

**For Development/Testing:**
```bash
ENABLE_OTP_TESTING_MODE=true
```
- OTP codes will appear in toast notifications
- No emails/SMS will be sent
- Perfect for local testing

**For Production:**
```bash
ENABLE_OTP_TESTING_MODE=false
```
- Real emails and SMS will be sent
- OTP codes NOT shown in responses
- Secure production mode

---

## 📊 Cost Estimation

### SendGrid (Email)
- **Free Tier:** 100 emails/day forever
- **Essentials:** $19.95/month for 50,000 emails
- **Recommendation:** Free tier is sufficient for starting

### MSG91 (India SMS)
- **Pay-as-you-go:** ₹0.15 - ₹0.20 per SMS
- **100 users/day:** ₹30 - ₹40/day = ₹900 - ₹1,200/month
- **1000 users/day:** ₹300 - ₹400/day = ₹9,000 - ₹12,000/month

### Twilio (International)
- **Pay-as-you-go:** $0.0079 per SMS (India)
- **100 users/day:** $1.58/day = ~$47/month
- **1000 users/day:** $15.8/day = ~$474/month

---

## 🔐 Security Best Practices

1. **Never commit API keys to git**
   ```bash
   # Already in .gitignore
   backend/.env
   ```

2. **Use environment variables in production**
   - Set via hosting platform (Vercel, Railway, AWS, etc.)
   - Never hardcode in code

3. **Rotate API keys regularly**
   - Every 3-6 months minimum
   - Immediately if suspected compromise

4. **Monitor usage**
   - Check SendGrid dashboard daily
   - Set up billing alerts on MSG91/Twilio

5. **Rate limiting**
   - Already implemented: OTP expires in 10 minutes
   - Consider adding: Max 3 OTP requests per hour per user

---

## ✅ Verification Checklist

Before going live, verify:

- [ ] SendGrid API key is valid
- [ ] Sender email is verified in SendGrid
- [ ] MSG91/Twilio credentials are correct
- [ ] SMS template is approved (MSG91)
- [ ] Test registration with real email/phone
- [ ] OTP arrives via both email AND SMS
- [ ] OTP verification works correctly
- [ ] `ENABLE_OTP_TESTING_MODE=false` in production
- [ ] Backend logs show successful sends
- [ ] Monitor first 10-20 real users

---

## 🐛 Troubleshooting

### Email not received?
1. Check SendGrid dashboard for delivery status
2. Look in spam/junk folder
3. Verify sender email is authenticated
4. Check backend logs: `tail -f /var/log/supervisor/backend.err.log`

### SMS not received?
1. **MSG91:** Check template approval status
2. **MSG91:** Verify phone number format (+91XXXXXXXXXX)
3. **Twilio:** Check console for delivery status
4. **Twilio:** Trial accounts can only send to verified numbers
5. Check backend logs for API errors

### OTP verification fails?
1. Check if OTP is expired (10 minutes)
2. Verify OTP is entered correctly
3. Check MongoDB for OTP records: `db.otp_verifications.find()`
4. User might be trying to reuse old OTP

### Backend errors?
```bash
# Check logs
tail -f /var/log/supervisor/backend.err.log

# Common issues:
# - Missing API keys
# - Invalid credentials
# - Network connectivity
# - SMS template not approved
```

---

## 📱 SMS Template Examples

### MSG91 Template (Hindi + English)
```
Your CalmSphere AI OTP: {OTP}. आपका OTP: {OTP}. Valid for 10 minutes. कभी साझा न करें। - CalmSphere
```

### Twilio Message (Set in code)
```
CalmSphere AI - Your verification code is: {OTP}

This code will expire in 10 minutes. Never share this code with anyone.

Need support? Call KIRAN: 1800-599-0019
```

---

## 🌟 Production Optimization

### Improve Deliverability

**Email (SendGrid):**
1. Use dedicated IP address ($89.95/month for high volume)
2. Set up custom domain authentication (SPF, DKIM, DMARC)
3. Warm up sending gradually (don't send 10,000 emails on day 1)
4. Monitor bounce rates and unsubscribes

**SMS (MSG91):**
1. Use promotional route for marketing (cheaper)
2. Use transactional route for OTPs (higher priority)
3. Add sender ID approval for brand name
4. Monitor delivery reports

### Reduce Costs

1. **Implement OTP caching:**
   - Allow OTP resend only after 1 minute
   - Max 3 attempts per session

2. **Smart channel selection:**
   - Send email first
   - Send SMS only if user requests resend
   - Saves ~50% SMS costs

3. **Batch processing:**
   - SendGrid supports bulk sending
   - Can reduce costs at scale

---

## 📞 Support Contacts

**SendGrid Support:**
- Email: support@sendgrid.com
- Docs: https://docs.sendgrid.com/

**MSG91 Support:**
- Phone: +91-9650607455
- Email: support@msg91.com
- Docs: https://docs.msg91.com/

**Twilio Support:**
- Support: https://www.twilio.com/help
- Docs: https://www.twilio.com/docs

---

## 🎉 You're Ready!

Your CalmSphere AI platform now has production-grade OTP authentication with:
✅ Secure email delivery via SendGrid
✅ Reliable SMS delivery via MSG91/Twilio
✅ Testing mode for development
✅ Beautiful HTML email templates
✅ India-localized phone support
✅ Crisis resources in communications

**Next Steps:**
1. Set up monitoring and alerts
2. Test with real users
3. Monitor delivery rates
4. Optimize based on usage patterns

**Questions?** Check backend logs or contact your development team.
