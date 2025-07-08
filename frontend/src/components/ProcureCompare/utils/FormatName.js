// frontend/src/components/ProcureCompare/utils/FormatName.js
export const formatEmailToName = (email) => {
    if (!email || typeof email !== 'string') return 'Bilinmeyen';
  
    const [namePart] = email.split('@');
    const parts = namePart.split('.');
  
    return parts
      .map(p => p.charAt(0).toUpperCase() + p.slice(1))
      .join(' ');
  };
  