import { Link } from "react-router-dom";

function Register() {
  return (
    <div className="auth-container">
      <h1>AI Memory Search Engine</h1>

      <h2>Register Page</h2>

      <p>
        Registration form coming next...
      </p>

      <Link to="/login">
        Back to Login
      </Link>
    </div>
  );
}

export default Register;