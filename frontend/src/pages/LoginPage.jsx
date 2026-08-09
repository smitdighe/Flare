import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext.jsx';
import AuthShell, { AuthBackLink, AuthError, AuthSubmit, FormField } from '../components/AuthShell.jsx';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);
    try { await login(email, password); navigate('/dashboard'); }
    catch (err) { setError(err.message || 'Unable to authenticate'); }
    finally { setLoading(false); }
  };

  return <AuthShell eyebrow="IDENTITY GATE // 01" title={<>See the signal.<br /><span className="text-amber">Own the response.</span></>} description="Sign in to the Flare command center and move from alert to action without losing the thread." footer={<><span>New operator?</span> <Link to="/register">Create an account <span aria-hidden="true">↗</span></Link><AuthBackLink /></>}>
    <div className="auth-heading"><h2>Operator sign in</h2><p>Use your Flare credentials to continue.</p></div>
    {error && <AuthError>{error}</AuthError>}
    <form onSubmit={handleSubmit} className="auth-form">
      <FormField label="Work email" id="login-email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" placeholder="operator@company.com" required />
      <FormField label="Password" id="login-password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" placeholder="••••••••••••" required />
      <div className="auth-options"><label className="auth-check"><input type="checkbox" /> <span>Keep me signed in</span></label><button type="button" className="auth-link-button" onClick={() => setError('Password recovery is not enabled in this environment.')}>Forgot password?</button></div>
      <AuthSubmit loading={loading}>Enter command center</AuthSubmit>
    </form>
  </AuthShell>;
}
