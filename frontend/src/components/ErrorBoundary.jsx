import React, { Component } from "react";

export class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Uncaught error in component tree:", error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="alert-banner" role="alert" style={{ margin: "2rem auto", maxWidth: "600px" }}>
          <div className="alert-body">
            <span className="alert-title">Application error</span>
            <span className="alert-desc">
              {this.state.error?.message || "An unexpected error occurred."}
            </span>
          </div>
          <button type="button" className="btn-sm" onClick={this.handleReset}>
            Reload
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
