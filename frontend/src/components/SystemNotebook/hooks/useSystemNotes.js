// frontend/src/components/SystemNotebook/hooks/useSystemNotes.js

import { useState, useEffect, useCallback } from 'react';
import {
  fetchSystemNotes,
  createSystemNote,
  updateSystemNote,
  deleteSystemNote,
  triggerGithubSync
} from '../api/systemNoteApi';

const useSystemNotes = () => {
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({});
  const [error, setError] = useState(null);

  const loadNotes = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchSystemNotes(filters);
      setNotes(data.results || []);
    } catch (err) {
      console.error('useSystemNotes HATA:', err);
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadNotes();
  }, [loadNotes]);

  const refresh = () => loadNotes();

  const applyFilters = (newFilters) => {
    // Filtreler komple sıfırlanarak yenileri set edilir
    setFilters({ ...newFilters });
  };

  const createNote = async (noteData) => {
    const created = await createSystemNote(noteData);
    refresh();
    return created;
  };

  const updateNote = async (id, noteData) => {
    const updated = await updateSystemNote(id, noteData);
    refresh();
    return updated;
  };

  const removeNote = async (id) => {
    await deleteSystemNote(id);
    refresh();
  };

  const syncFromGithub = async () => {
    await triggerGithubSync();
    refresh();
  };

  return {
    notes,
    loading,
    error,
    filters,
    applyFilters,
    refresh,
    createNote,
    updateNote,
    removeNote,
    syncFromGithub
  };
};

export default useSystemNotes;
