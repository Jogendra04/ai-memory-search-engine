import { useEffect, useState } from "react";
import {
  getMemories,
  deleteMemory,
} from "../../services/api";

function MemoryList({ refresh }) {
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadMemories = async () => {
    try {
      const data = await getMemories();
      setMemories(data.memories || []);
    } catch (error) {
      console.error(error);
      alert(error.message || "Failed to load memories.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setLoading(true);

    const fetchMemories = async () => {
      await loadMemories();
    };

    fetchMemories();
  }, [refresh]);

  const handleDelete = async (id) => {
    const confirmed = window.confirm(
      "Delete this memory?"
    );

    if (!confirmed) return;

    try {
      setLoading(true);

      await deleteMemory(id);

      await loadMemories();

      alert("Memory deleted successfully.");
    } catch (error) {
      console.error(error);
      alert(error.message || "Failed to delete memory.");
    }
  };

  return (
    <div className="memory-list">

      <h2>Saved Memories</h2>

      {loading ? (
        <p>Loading memories...</p>
      ) : memories.length === 0 ? (
        <p>No memories saved yet.</p>
      ) : (
        memories.map((memory) => (
          <div
            key={memory.id}
            className="memory-card"
          >
            <div className="memory-header">

              <h3>{memory.title}</h3>

              <button
                className="delete-button"
                onClick={() => handleDelete(memory.id)}
              >
                Delete
              </button>

            </div>

            <p>{memory.content}</p>

            {memory.tags?.length > 0 && (
              <div className="tags">
                {memory.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="tag"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            )}

          </div>
        ))
      )}

    </div>
  );
}

export default MemoryList;