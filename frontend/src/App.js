import React, { useState, useRef } from 'react';
import './App.css';
import { X } from 'lucide-react';
// MUDANÇA AQUI: Adicionando a extensão .gif ao import
import ExameGif from './exame.gif'; // Importa o GIF como uma variável (URL)

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  // ... (toda a lógica handleFileChange, handleDrop, etc., continua a mesma)
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setError('');
      setResults([]);
    } else {
      setSelectedFile(null);
      setError('Por favor, selecione um arquivo PDF válido.');
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();
    event.currentTarget.classList.remove('drag-over');
    const file = event.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setError('');
      setResults([]);
    } else {
      setSelectedFile(null);
      setError('Por favor, solte um arquivo PDF válido.');
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();
    event.currentTarget.classList.add('drag-over');
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    event.stopPropagation();
    event.currentTarget.classList.remove('drag-over');
  };

  const handleClearFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    setResults([]);
    setError('');
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!selectedFile) {
      setError('Por favor, selecione um arquivo PDF.');
      return;
    }

    setIsLoading(true);
    setError('');
    setResults([]);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('http://127.0.0.1:8000/explain-pdf/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail?.error || errorData.detail || `Erro ${response.status}`);
      }

      const data = await response.json();
      setResults(data.explanations);

    } catch (err) {
      console.error("Erro na requisição:", err);
      setError(err.message || 'Ocorreu um erro ao se comunicar com o servidor.');
    } finally {
      setIsLoading(false);
    }
  };


  return (
    <div className="container">
      <header className="header">
        <div className="header-title-container">
          {/* MUDANÇA AQUI: Usando a variável importada ExameGif */}
          <img src={ExameGif} alt="Med-Bot Logo" className="header-logo" />
          <h1>Med-Bot</h1>
        </div>
        <p>Seu assistente para descomplicar exames médicos.</p>
      </header>

      <main className="main-content">
        <div 
          className="upload-zone"
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
        >
          {selectedFile ? (
            <div className="file-preview">
              <p className="file-name">{selectedFile.name}</p>
              <button className="clear-file-button" onClick={handleClearFile}>
                <X size={16} />
              </button>
            </div>
          ) : (
            <>
              {/* O ícone de upload foi removido para manter o design clean */}
              <p className="upload-instructions">
                Arraste e solte seu PDF aqui, ou <span className="browse-link" onClick={() => fileInputRef.current.click()}>procure um arquivo</span>
              </p>
              <input
                type="file"
                ref={fileInputRef}
                accept=".pdf"
                onChange={handleFileChange}
                style={{ display: 'none' }}
              />
            </>
          )}
        </div>

        {error && <p className="status-message error">{error}</p>}
        {isLoading && (
          <div className="loading-indicator">
            <div className="spinner"></div>
            <p>Analisando o documento com IA...</p>
          </div>
        )}

        <button
          className="process-button"
          onClick={handleSubmit}
          disabled={!selectedFile || isLoading}
        >
          {isLoading ? 'Analisando...' : 'Explicar Exame'}
        </button>

        {results.length > 0 && (
          <div className="results-display">
            <h2>Termos Explicados:</h2>
            {results.map((item, index) => (
              <div key={index} className="result-item">
                <h3>{item.term}</h3>
                <p>{item.explanation}</p>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;