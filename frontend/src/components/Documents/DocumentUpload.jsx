import { useState } from "react";
import { uploadDocument } from "../../services/api";

function DocumentUpload({ onUploadSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");

  const handleFileChange = (event) => {
    const file = event.target.files[0];

    setUploadMessage("");

    if (!file) {
      setSelectedFile(null);
      return;
    }

    if (file.type !== "application/pdf") {
      setUploadMessage("Please select a PDF file.");
      setSelectedFile(null);
      return;
    }

    setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadMessage("Please select a PDF file.");
      return;
    }

    setUploadLoading(true);

    try {
      const data = await uploadDocument(selectedFile);

      setUploadMessage(
        data.message || "Document uploaded successfully!"
      );

      setSelectedFile(null);

      const input = document.getElementById("pdf-upload");

      if (input) {
        input.value = "";
      }

      if (onUploadSuccess) {
        onUploadSuccess();
      }

    } catch (error) {
      console.error(error);
      setUploadMessage("Upload failed.");
    }

    setUploadLoading(false);
  };

  return (
    <div className="upload-section">

      <h2>Documents</h2>

      <input
        id="pdf-upload"
        type="file"
        accept=".pdf"
        onChange={handleFileChange}
      />

      {selectedFile && (
        <p>Selected: {selectedFile.name}</p>
      )}

      <button
        onClick={handleUpload}
        disabled={uploadLoading}
      >
        {uploadLoading ? "Processing..." : "Upload Document"}
      </button>

      {uploadMessage && (
        <p>{uploadMessage}</p>
      )}

    </div>
  );
}

export default DocumentUpload;