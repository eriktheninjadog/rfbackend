import React, { useState } from 'react';

const TaskCreator = () => {
  const [task, setTask] = useState({
    level: 1,
    scenario_template: '',
    target_skills: [],
    target_vocabulary: [],
    complexity: 'simple_linear',
    prerequisites: []
  });

  const [newSkill, setNewSkill] = useState('');
  const [newVocab, setNewVocab] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const API_BASE = 'http://localhost:5000/api/dmapi';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const response = await fetch(`${API_BASE}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(task)
      });

      const data = await response.json();

      if (response.ok) {
        alert('任務創建成功！');
        // Reset form
        setTask({
          level: 1,
          scenario_template: '',
          target_skills: [],
          target_vocabulary: [],
          complexity: 'simple_linear',
          prerequisites: []
        });
      } else {
        alert(`錯誤: ${data.error}`);
      }
    } catch (error) {
      alert(`網絡錯誤: ${error.message}`);
    }

    setIsSubmitting(false);
  };

  const addSkill = () => {
    if (newSkill.trim() && !task.target_skills.includes(newSkill)) {
      setTask(prev => ({
        ...prev,
        target_skills: [...prev.target_skills, newSkill.trim()]
      }));
      setNewSkill('');
    }
  };

  const addVocab = () => {
    if (newVocab.trim() && !task.target_vocabulary.includes(newVocab)) {
      setTask(prev => ({
        ...prev,
        target_vocabulary: [...prev.target_vocabulary, newVocab.trim()]
      }));
      setNewVocab('');
    }
  };

  const removeSkill = (skill) => {
    setTask(prev => ({
      ...prev,
      target_skills: prev.target_skills.filter(s => s !== skill)
    }));
  };

  const removeVocab = (vocab) => {
    setTask(prev => ({
      ...prev,
      target_vocabulary: prev.target_vocabulary.filter(v => v !== vocab)
    }));
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '20px' }}>
      <h2>創建新任務</h2>
      
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
        <div>
          <label>級別:</label>
          <select
            value={task.level}
            onChange={(e) => setTask(prev => ({ ...prev, level: parseInt(e.target.value) }))}
            style={{ width: '100%', padding: '8px' }}
          >
            <option value={1}>Level 1</option>
            <option value={2}>Level 2</option>
            <option value={3}>Level 3</option>
          </select>
        </div>

        <div>
          <label>情境模板:</label>
          <textarea
            value={task.scenario_template}
            onChange={(e) => setTask(prev => ({ ...prev, scenario_template: e.target.value }))}
            placeholder="例如: 你朋友{name}喺{location}..."
            style={{ width: '100%', height: '100px', padding: '8px' }}
            required
          />
        </div>

        <div>
          <label>目標技能:</label>
          <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
            <input
              value={newSkill}
              onChange={(e) => setNewSkill(e.target.value)}
              placeholder="例如: giving_advice"
              style={{ flex: 1, padding: '8px' }}
            />
            <button type="button" onClick={addSkill}>添加</button>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
            {task.target_skills.map(skill => (
              <span key={skill} style={{ 
                backgroundColor: '#e3f2fd', 
                padding: '4px 8px', 
                borderRadius: '4px',
                cursor: 'pointer'
              }} onClick={() => removeSkill(skill)}>
                {skill} ×
              </span>
            ))}
          </div>
        </div>

        <div>
          <label>目標詞彙:</label>
          <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
            <input
              value={newVocab}
              onChange={(e) => setNewVocab(e.target.value)}
              placeholder="例如: 建議"
              style={{ flex: 1, padding: '8px' }}
            />
            <button type="button" onClick={addVocab}>添加</button>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
            {task.target_vocabulary.map(vocab => (
              <span key={vocab} style={{ 
                backgroundColor: '#f1f8e9', 
                padding: '4px 8px', 
                borderRadius: '4px',
                cursor: 'pointer'
              }} onClick={() => removeVocab(vocab)}>
                {vocab} ×
              </span>
            ))}
          </div>
        </div>

        <div>
          <label>複雜度:</label>
          <select
            value={task.complexity}
            onChange={(e) => setTask(prev => ({ ...prev, complexity: e.target.value }))}
            style={{ width: '100%', padding: '8px' }}
          >
            <option value="simple_linear">Simple Linear</option>
            <option value="simple_branching">Simple Branching</option>
            <option value="complex_branching">Complex Branching</option>
          </select>
        </div>

        <button 
          type="submit" 
          disabled={isSubmitting}
          style={{
            padding: '12px',
            backgroundColor: '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '16px'
          }}
        >
          {isSubmitting ? '創建中...' : '創建任務'}
        </button>
      </form>
    </div>
  );
};

export default TaskCreator;
