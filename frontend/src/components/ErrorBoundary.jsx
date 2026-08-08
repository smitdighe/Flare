import { Component } from 'react';
import Icon from './Icon.jsx';

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('[ErrorBoundary]', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen items-center justify-center bg-ink-950 p-8">
          <div className="max-w-md border border-line-strong bg-ink-900 p-8">
            <div className="mb-4 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center border border-red bg-red/10">
                <Icon name="error" size={20} className="text-red" />
              </div>
              <div>
                <h2 className="font-mono-ui text-sm font-semibold text-paper">Something went wrong</h2>
                <p className="font-mono-ui text-[10px] text-ash-dark">The application encountered an unexpected error</p>
              </div>
            </div>
            <div className="mt-4 border border-line bg-ink-950 p-3">
              <pre className="font-mono-ui text-[10px] text-ash-dark overflow-auto">
                {this.state.error?.message || 'Unknown error'}
              </pre>
            </div>
            <button
              type="button"
              className="terminal-button mt-6 inline-flex items-center gap-2 px-4 py-2 font-mono-ui text-[10px] uppercase tracking-[0.1em]"
              onClick={() => this.setState({ hasError: false, error: null })}
            >
              <Icon name="refresh" size={14} />
              Try again
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
