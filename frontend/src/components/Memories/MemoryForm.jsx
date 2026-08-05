import { useState } from "react";
import { saveMemory } from "../../services/api";

function MemoryForm({ onMemorySaved }) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [tags, setTags] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    if (!title.trim()) {
      alert("Enter a title");
      return;
    }

    if (!content.trim()) {
      alert("Enter memory content");
      return;
    }

    const tagList = tags
      .split(",")
      .map(tag => tag.trim())
      .filter(tag => tag.length > 0);

    setLoading(true);

    try {

      await saveMemory({
        title,
        content,
        tags: tagList,
      });

      setTitle("");
      setContent("");
      setTags("");

      if (onMemorySaved) {
        onMemorySaved();
      }

      alert("Memory saved!");

    } catch (error) {
      console.error(error);
      alert("Failed to save memory.");
    }

    setLoading(false);
  };

  return (
    <div className="memory-form">

      <h2>Add Memory</h2>

      <input
        type="text"
        placeholder="Memory title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />

      <textarea
        rows={5}
        placeholder="Write your memory..."
        value={content}
        onChange={(e) => setContent(e.target.value)}
      />

      <input
        type="text"
        placeholder="Tags: ai, python, project"
        value={tags}
        onChange={(e) => setTags(e.target.value)}
      />

      <button
        onClick={handleSave}
        disabled={loading}
      >
        {loading ? "Saving..." : "Save Memory"}
      </button>

    </div>
  );
}

export default MemoryForm;