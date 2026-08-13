import { useState } from "react";
import { saveMemory } from "../../services/api";

function MemoryForm({ onMemorySaved }) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [tags, setTags] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSave = async (event) => {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (!title.trim()) {
      setError("Please enter a memory title.");
      return;
    }

    if (!content.trim()) {
      setError("Please enter memory content.");
      return;
    }

    const tagList = tags
      .split(",")
      .map((tag) => tag.trim())
      .filter((tag) => tag.length > 0);

    try {
      setLoading(true);

      await saveMemory({
        title: title.trim(),
        content: content.trim(),
        tags: tagList,
      });

      setTitle("");
      setContent("");
      setTags("");

      setSuccess("Memory saved successfully.");

      if (onMemorySaved) {
        onMemorySaved();
      }
    } catch (error) {
      console.error(
        "Failed to save memory:",
        error
      );

      setError(
        error.message ||
          "Failed to save memory."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="memory-form">

      <div className="section-heading">
        <div>
          <h2>Add Memory</h2>

          <p>
            Save information you want your AI to remember.
          </p>
        </div>
      </div>

      <form onSubmit={handleSave}>

        <label htmlFor="memory-title">
          Title
        </label>

        <input
          id="memory-title"
          type="text"
          placeholder="e.g. My AI project"
          value={title}
          onChange={(event) =>
            setTitle(event.target.value)
          }
          disabled={loading}
        />

        <label htmlFor="memory-content">
          Content
        </label>

        <textarea
          id="memory-content"
          rows={5}
          placeholder="Write something you want your AI to remember..."
          value={content}
          onChange={(event) =>
            setContent(event.target.value)
          }
          disabled={loading}
        />

        <label htmlFor="memory-tags">
          Tags
        </label>

        <input
          id="memory-tags"
          type="text"
          placeholder="ai, python, project"
          value={tags}
          onChange={(event) =>
            setTags(event.target.value)
          }
          disabled={loading}
        />

        <p className="field-hint">
          Separate multiple tags with commas.
        </p>

        <button
          type="submit"
          disabled={loading}
        >
          {loading
            ? "Saving..."
            : "Save Memory"}
        </button>

      </form>

      {error && (
        <div className="form-error">
          {error}
        </div>
      )}

      {success && (
        <div className="form-success">
          {success}
        </div>
      )}

    </div>
  );
}

export default MemoryForm;