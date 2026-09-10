import { useState } from "react";
import { Link } from "react-router-dom";

function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();

    setMessage("");
    setError("");
    setLoading(true);

    try {
      const response = await fetch(
        "https://ai-memory-search-engine.onrender.com/auth/forgot-password",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setError(
          data.detail ||
            "Unable to process your request."
        );
        return;
      }

      setMessage(
        "If an account exists with this email, a password reset link has been sent."
      );

      setEmail("");
    } catch (error) {
      console.error("Forgot password error:", error);

      setError(
        "Unable to connect to the server. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">

        {/* Brand */}
        <div className="auth-brand">
          <div className="auth-logo">
            AI
          </div>

          <div>
            <h1>AI Memory Search</h1>
            <span>
              Your personal knowledge system
            </span>
          </div>
        </div>

        {/* Heading */}
        <div className="auth-heading">
          <h2>Forgot your password?</h2>

          <p>
            Enter your email address and we'll
            send you a link to reset your password.
          </p>
        </div>

        {/* Success */}
        {message && (
          <div className="auth-success">
            {message}
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="auth-error">
            {error}
          </div>
        )}

        {/* Form */}
        <form
          className="auth-form"
          onSubmit={handleSubmit}
        >
          <div className="form-group">
            <label htmlFor="email">
              Email address
            </label>

            <input
              id="email"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
              disabled={loading}
              required
              autoComplete="email"
            />
          </div>

          <button
            className="auth-submit"
            type="submit"
            disabled={loading}
          >
            {loading
              ? "Sending..."
              : "Send Reset Link"}
          </button>
        </form>

        {/* Footer */}
        <div className="auth-footer">
          <span>
            Remember your password?
          </span>

          <Link to="/login">
            Back to Sign in
          </Link>
        </div>

      </div>
    </div>
  );
}

export default ForgotPassword;