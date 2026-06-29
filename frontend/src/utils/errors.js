/**
 * Safely extracts a string error message from an API request error,
 * including structured Pydantic/FastAPI validation arrays.
 */
export function getErrorMessage(err, defaultMsg = 'An error occurred') {
  if (!err) return defaultMsg;
  
  const detail = err.response?.data?.detail;
  
  // 1. FastAPI detail as simple string
  if (typeof detail === 'string') {
    return detail;
  }
  
  // 2. FastAPI/Pydantic validation errors (array of objects)
  if (Array.isArray(detail)) {
    return detail.map(d => {
      if (typeof d === 'object' && d !== null) {
        const locStr = d.loc ? d.loc.filter(x => x !== 'body' && x !== 'query').join('.') : '';
        return `${locStr ? locStr + ': ' : ''}${d.msg || JSON.stringify(d)}`;
      }
      return String(d);
    }).join(' | ');
  }
  
  // 3. Object details
  if (detail && typeof detail === 'object') {
    try {
      return JSON.stringify(detail);
    } catch {
      return String(detail);
    }
  }
  
  // 4. Custom backend message
  if (err.response?.data?.message) {
    return err.response.data.message;
  }
  
  // 5. General browser network/axios message
  if (err.message) {
    return err.message;
  }
  
  return defaultMsg;
}
