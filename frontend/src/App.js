import React, { useState, useRef } from 'react';
import './App.css';
import { X, ChevronDown, AlertTriangle, Activity } from 'lucide-react';
import ExameGif from './exame.gif';
import ReactMarkdown from 'react-markdown';

// O componente do Acordeão permanece o mesmo
const AccordionItem = ({ group, isOpen, onToggle }) => (
  <div className="result-group">
    <button className="group-title-button" onClick={onToggle}>
      <h3 className="group-title">{group.group_name}</h3>
      <ChevronDown className={`chevron-icon ${isOpen ? 'open' : ''}`} />
    </button>
    {isOpen && (
      <div className="group-content">
        {group.results.map((item, itemIndex) => (
          <div key={itemIndex} className={`result-item ${item.status_class}`}>
            <div className="result-header">
              <h4>{item.exame}</h4>
              <span className="result-value">{item.valor} {item.unidade}</span>
            </div>
            <div className="interpretation-text">
                <ReactMarkdown>{item.interpretacao}</ReactMarkdown>
            </div>
            
            {item.analise_ia && (
               <div className="ai-analysis">
                 <h5><Activity size={16} /> {item.analise_ia.titulo}</h5>
                 <div className="analysis-body">
                    <ReactMarkdown>{item.analise_ia.analise}</ReactMarkdown>
                 </div>
                 
                 <div className="recommendation">
                    <ReactMarkdown>{item.analise_ia.recomendacao}</ReactMarkdown>
                 </div>
                 <p className="disclaimer">
                    <AlertTriangle size={14} />
                    {item.analise_ia.alerta}
                 </p>
               </div>
            )}
          </div>
        ))}
      </div>
    )}
  </div>
);


function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  // MUDANÇA: O estado 'error' agora centraliza todas as mensagens de erro e aviso
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);
  const [age, setAge] = useState('');
  const [sex, setSex] = useState('');
  const [openGroups, setOpenGroups] = useState({});

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file); setError(''); setResults([]);
    } else {
      setSelectedFile(null); setError('Por favor, selecione um arquivo PDF válido.');
    }
  };

  const handleClearFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
    setResults([]); setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    // MUDANÇA: A validação agora usa o estado 'error'
    if (!age || !sex || !selectedFile) {
      setError('Por favor, preencha a idade, o sexo e selecione um arquivo para continuar.');
      return;
    }
    
    setIsLoading(true); 
    setError(''); 
    setResults([]); 
    setOpenGroups({});

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('idade', age);
    formData.append('sexo', sex);

    try {
      const response = await fetch('http://127.0.0.1:8000/analyze-pdf/', { method: 'POST', body: formData });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || `Erro do servidor: ${response.status}`);
      setResults(data.groups);
    } catch (err) {
      setError(err.message || 'Ocorreu um erro ao se comunicar com o servidor.');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleGroup = (index) => {
    setOpenGroups(prev => ({ ...prev, [index]: !prev[index] }));
  };

  const handleDrop = (e) => { e.preventDefault(); e.stopPropagation(); e.currentTarget.classList.remove('drag-over'); const file = e.dataTransfer.files[0]; if (file && file.type === 'application/pdf') { setSelectedFile(file); setError(''); setResults([]); } else { setSelectedFile(null); setError('Por favor, solte um arquivo PDF válido.'); } };
  const handleDragOver = (e) => { e.preventDefault(); e.stopPropagation(); e.currentTarget.classList.add('drag-over'); };
  const handleDragLeave = (e) => { e.preventDefault(); e.stopPropagation(); e.currentTarget.classList.remove('drag-over'); };

  return (
    <div className="container">
      <header className="header">
        <div className="header-title-container">
          <img src={ExameGif} alt="Med-Bot Logo" className="header-logo" />
          <h1>Med-Bot</h1>
        </div>
        <p>Seu assistente para descomplicar e analisar exames médicos.</p>
      </header>

      <main className="main-content">
        <div className="user-inputs">
          <div className="input-group">
            <label htmlFor="age">Sua Idade</label>
            <input 
              type="text" 
              inputMode="numeric" 
              pattern="[0-9]*" 
              id="age" 
              value={age} 
              onChange={(e) => setAge(e.target.value.replace(/[^0-9]/g, ''))} 
              placeholder="Ex: 35" 
            />
          </div>
          <div className="input-group">
            <label htmlFor="sex">Sexo Biológico</label>
            <div className="select-wrapper">
              <select id="sex" value={sex} onChange={(e) => setSex(e.target.value)}>
                <option value="" disabled>Selecione...</option>
                <option value="masculino">Masculino</option>
                <option value="feminino">Feminino</option>
              </select>
            </div>
          </div>
        </div>
        
        {/* MUDANÇA: O 'error' agora renderiza todas as mensagens de erro/aviso */}
        {error && (
            <div className="status-message error">
                <AlertTriangle size={18} />
                {error}
            </div>
        )}

        <div className="upload-zone" onDrop={handleDrop} onDragOver={handleDragOver} onDragLeave={handleDragLeave}>
          {selectedFile ? (
            <div className="file-preview">
              <p className="file-name">{selectedFile.name}</p>
              <button className="clear-file-button" onClick={handleClearFile}><X size={16} /></button>
            </div>
          ) : (
            <p className="upload-instructions">Arraste e solte seu PDF aqui, ou <span className="browse-link" onClick={() => fileInputRef.current.click()}>procure um arquivo</span></p>
          )}
           <input type="file" ref={fileInputRef} accept=".pdf" onChange={handleFileChange} style={{ display: 'none' }} />
        </div>

        <button className="process-button" onClick={handleSubmit} disabled={isLoading}>
          {isLoading ? 'Analisando...' : 'Analisar Exame'}
        </button>
        
        {isLoading && (<div className="loading-indicator"><div className="spinner"></div><p>Analisando o documento com IA...</p></div>)}

        {results.length > 0 && (
          <div className="results-display">
            <h2>Resultados da Análise</h2>
            {results.map((group, groupIndex) => (
              <AccordionItem 
                key={groupIndex}
                group={group}
                isOpen={!!openGroups[groupIndex]}
                onToggle={() => toggleGroup(groupIndex)}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;