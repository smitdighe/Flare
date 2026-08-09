import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext.jsx';
import AuthShell, { AuthBackLink, AuthError, AuthSubmit, FormField } from '../components/AuthShell.jsx';

export default function RegisterPage() {
  const [name, setName] = useState(''); const [email, setEmail] = useState(''); const [password, setPassword] = useState(''); const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState(''); const [loading, setLoading] = useState(false); const { register } = useAuth(); const navigate = useNavigate();
  const handleSubmit = async (event) => { event.preventDefault(); setError(''); if (password !== confirmPassword) return setError('Passwords do not match'); if (password.length < 8) return setError('Password must be at least 8 characters'); setLoading(true); try { await register(email, name, password); navigate('/dashboard'); } catch (err) { setError(err.message || 'Unable to create account'); } finally { setLoading(false); } };
  return <AuthShell eyebrow="IDENTITY GATE // 02" title={<>Build a calmer<br /><span className="text-amber">security practice.</span></>} description="Create an operator account for the Flare command center. Your first workspace is ready when you are." footer={<><span>Already registered?</span> <Link to="/login">Sign in <span aria-hidden="true">↗</span></Link><AuthBackLink /></>}>
    <div className="auth-heading"><h2>Create operator account</h2><p>Provision access to the live triage workspace.</p></div>
    {error && <AuthError>{error}</AuthError>}
    <form onSubmit={handleSubmit} className="auth-form">
      <FormField label="Operator name" id="register-name" type="text" value={name} onChange={(e) => setName(e.target.value)} autoComplete="name" placeholder="Alex Morgan" required />
      <FormField label="Work email" id="register-email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" placeholder="operator@company.com" required />
      <FormField label="Password" id="register-password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="new-password" placeholder="Minimum 8 characters" minLength={8} required />
      <FormField label="Confirm password" id="register-confirm" type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} autoComplete="new-password" placeholder="Repeat password" required />
      <p className="auth-note"><span className="status-pip" /> Passwords are hashed and never exposed to the workspace.</p>
      <AuthSubmit loading={loading}>Create operator account</AuthSubmit>
    </form>
  </AuthShell>;
}
