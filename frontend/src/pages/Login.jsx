import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();

    setError("");
    setLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/auth/login",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email,
            password,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setError(
          data.detail ||
            "Invalid email or password."
        );
        return;
      }

      localStorage.setItem(
        "access_token",
        data.access_token
      );

      navigate("/dashboard");
    } catch (error) {
      console.error(error);

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
            <span>Your personal knowledge system</span>
          </div>

        </div>


        {/* Heading */}

        <div className="auth-heading">

          <h2>Welcome back</h2>

          <p>
            Sign in to access your memories,
            documents, and AI assistant.
          </p>

        </div>


        {/* Error */}

        {error && (
          <div className="auth-error">
            {error}
          </div>
        )}


        {/* Form */}

        <form
          className="auth-form"
          onSubmit={handleLogin}
        >

          {/* Email */}

          <div className="form-group">

            <label htmlFor="email">
              Email address
            </label>

            <input
              id="email"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) =>
                setEmail(e.target.value)
              }
              required
              autoComplete="email"
            />

          </div>


          {/* Password */}

          <div className="form-group">

            <div className="password-label-row">

              <label htmlFor="password">
                Password
              </label>

            </div>

            <div className="password-input-wrapper">

              <input
                id="password"
                type={
                  showPassword
                    ? "text"
                    : "password"
                }
                placeholder="Enter your password"
                value={password}
                onChange={(e) =>
                  setPassword(e.target.value)
                }
                required
                autoComplete="current-password"
              />

              <button
                type="button"
                className="password-toggle"
                onClick={() =>
                  setShowPassword(
                    !showPassword
                  )
                }
              >
                {showPassword
                  ? "Hide"
                  : "Show"}
              </button>

            </div>

          </div>


          {/* Submit */}

          <button
            type="submit"
            className="auth-submit"
            disabled={loading}
          >
            {loading
              ? "Signing in..."
              : "Sign in"}
          </button>

        </form>


        {/* Register */}

        <div className="auth-footer">

          <span>
            Don't have an account?
          </span>

          <Link to="/register">
            Create an account
          </Link>

        </div>


        <p className="auth-bottom-text">
          Secure access to your personal AI
          knowledge base.
        </p>

      </div>

    </div>
  );
}

export default Login;