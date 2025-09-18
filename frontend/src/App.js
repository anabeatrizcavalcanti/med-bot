import React, { useState } from 'react';
import './App.css';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [results, setResults] = useState([]); // Mudou de extractedTerms para results
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setError('');
    setResults([]);
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
      // O endpoint mudou para /explain-pdf/
      const response = await fetch('http://127.0.0.1:8000/explain-pdf/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail?.error || errorData.detail || `Erro ${response.status}`);
      }

      const data = await response.json();
      setResults(data.explanations); // A resposta agora está em 'explanations'

    } catch (err) {
      setError(err.message || 'Ocorreu um erro ao se comunicar com o servidor.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Med-Bot: Explicador de Exames</h1>
        <p>Envie um documento de exame (PDF) para entender os termos técnicos.</p>
        
        <form onSubmit={handleSubmit}>
          <input type="file" accept=".pdf" onChange={handleFileChange} />
          <button type="submit" disabled={!selectedFile || isLoading}>
            {isLoading ? 'Analisando...' : 'Explicar Documento'}
          </button>
        </form>

        {error && <p className="error-message">{error}</p>}
      </header>
      
      <main className="results-section">
        {results.length > 0 && (
          <div className="results-container">
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