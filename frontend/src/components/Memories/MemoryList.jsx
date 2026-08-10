import { useEffect, useState } from "react";

import {
  getMemories,
  deleteMemory,
  updateMemory,
} from "../../services/api";


function MemoryList({ refresh }) {

  const [memories, setMemories] = useState([]);

  const [loading, setLoading] = useState(false);

  const [editingId, setEditingId] = useState(null);

  const [editTitle, setEditTitle] = useState("");
  const [editContent, setEditContent] = useState("");
  const [editTags, setEditTags] = useState("");


  const loadMemories = async () => {

    try {

      setLoading(true);

      const data = await getMemories();

      setMemories(
        data.memories || []
      );

    } catch (error) {

      console.error(error);

      alert(
        error.message ||
        "Failed to load memories."
      );

    } finally {

      setLoading(false);

    }
  };


  useEffect(() => {

    loadMemories();

  }, [refresh]);


  // ==========================================
  // Start editing
  // ==========================================

  const handleEdit = (memory) => {

    setEditingId(memory.id);

    setEditTitle(
      memory.title || ""
    );

    setEditContent(
      memory.content || ""
    );

    setEditTags(
      (memory.tags || []).join(", ")
    );
  };


  // ==========================================
  // Cancel editing
  // ==========================================

  const handleCancelEdit = () => {

    setEditingId(null);

    setEditTitle("");
    setEditContent("");
    setEditTags("");
  };


  // ==========================================
  // Save edited memory
  // ==========================================

  const handleUpdate = async () => {

    if (!editTitle.trim()) {

      alert("Enter a title.");

      return;
    }

    if (!editContent.trim()) {

      alert("Enter memory content.");

      return;
    }


    const tagList = editTags
      .split(",")
      .map((tag) => tag.trim())
      .filter(
        (tag) => tag.length > 0
      );


    try {

      setLoading(true);

      await updateMemory(
        editingId,
        {
          title: editTitle,
          content: editContent,
          tags: tagList,
        }
      );


      setEditingId(null);

      setEditTitle("");
      setEditContent("");
      setEditTags("");


      await loadMemories();


      alert(
        "Memory updated successfully."
      );

    } catch (error) {

      console.error(error);

      alert(
        error.message ||
        "Failed to update memory."
      );

    } finally {

      setLoading(false);

    }
  };


  // ==========================================
  // Delete memory
  // ==========================================

  const handleDelete = async (id) => {

    const confirmed =
      window.confirm(
        "Delete this memory?"
      );


    if (!confirmed) {
      return;
    }


    try {

      setLoading(true);

      await deleteMemory(id);

      await loadMemories();

      alert(
        "Memory deleted successfully."
      );

    } catch (error) {

      console.error(error);

      alert(
        error.message ||
        "Failed to delete memory."
      );

    } finally {

      setLoading(false);

    }
  };


  return (

    <div>

      <h2>Saved Memories</h2>


      {loading && (
        <p>Loading memories...</p>
      )}


      {!loading &&
        memories.length === 0 && (
          <p>
            No memories saved yet.
          </p>
        )}


      {!loading &&
        memories.map((memory) => (

          <div
            key={memory.id}
            className="memory-card"
          >

            {editingId === memory.id ? (

              // ==================================
              // EDIT MODE
              // ==================================

              <div>

                <h3>Edit Memory</h3>


                <input
                  type="text"
                  value={editTitle}
                  onChange={(e) =>
                    setEditTitle(
                      e.target.value
                    )
                  }
                  placeholder="Memory title"
                />


                <textarea
                  rows={5}
                  value={editContent}
                  onChange={(e) =>
                    setEditContent(
                      e.target.value
                    )
                  }
                  placeholder="Memory content"
                />


                <input
                  type="text"
                  value={editTags}
                  onChange={(e) =>
                    setEditTags(
                      e.target.value
                    )
                  }
                  placeholder="Tags: ai, python, project"
                />


                <button
                  onClick={handleUpdate}
                  disabled={loading}
                >
                  {loading
                    ? "Updating..."
                    : "Update Memory"}
                </button>


                <button
                  onClick={
                    handleCancelEdit
                  }
                  disabled={loading}
                >
                  Cancel
                </button>

              </div>

            ) : (

              // ==================================
              // VIEW MODE
              // ==================================

              <div>

                <div className="memory-header">

                  <h3>
                    {memory.title}
                  </h3>


                  <div>

                    <button
                      onClick={() =>
                        handleEdit(
                          memory
                        )
                      }
                    >
                      Edit
                    </button>


                    <button
                      className="delete-button"
                      onClick={() =>
                        handleDelete(
                          memory.id
                        )
                      }
                    >
                      Delete
                    </button>

                  </div>

                </div>


                <p>
                  {memory.content}
                </p>


                {memory.tags?.length > 0 && (

                  <div className="tags">

                    {memory.tags.map(
                      (tag, index) => (

                        <span
                          key={index}
                          className="tag"
                        >
                          #{tag}
                        </span>

                      )
                    )}

                  </div>

                )}

              </div>

            )}

          </div>

        ))}

    </div>
  );
}


export default MemoryList;