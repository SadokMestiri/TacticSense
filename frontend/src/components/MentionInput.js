import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';

const MentionInput = ({ value, onChange, onMentionsChange, placeholder, className }) => {
  const [inputValue, setInputValue] = useState(value || '');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  // activeQuery can be:
  // null: No active mention search
  // '': User typed '@', show all taggable
  // 'abc': User typed '@abc', filter by 'abc'
  const [activeQuery, setActiveQuery] = useState(null); 
  const textareaRef = useRef(null);
  const suggestionsRef = useRef(null);

  // Construct media URL, similar to Home.js/Profile.js
  const constructMediaUrl = (urlPath) => {
    if (!urlPath) return '';
    if (urlPath.startsWith('http://') || urlPath.startsWith('https://')) {
      return urlPath;
    }
    const baseUrl = process.env.REACT_APP_BASE_URL || '';
    return `${baseUrl}${urlPath.startsWith('/') ? '' : '/'}${urlPath}`;
  };

  useEffect(() => {
    // Sync internal state if the prop `value` changes from outside
    if (value !== inputValue) {
        setInputValue(value || '');
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  const fetchTaggableUsers = useCallback(async (query) => {
    // query can be an empty string '' to fetch all, or a string to filter
    try {
      const token = Cookies.get('token');
      let url = `${process.env.REACT_APP_BASE_URL}/users/taggable`;
      
      // Only add q parameter if the query string is not empty
      if (query && query.length > 0) {
        url += `?q=${query}`;
      }
      // If query is '', the url remains /users/taggable (backend should handle this as "fetch all taggable")

      const response = await axios.get(url, { headers: { Authorization: `Bearer ${token}` } });
      setSuggestions(response.data || []);
      setShowSuggestions(response.data && response.data.length > 0); // Show if there are suggestions
    } catch (error) {
      console.error("Error fetching taggable users:", error);
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, []); // Empty dependency array as it doesn't rely on component state/props that change

  useEffect(() => {
    const handler = setTimeout(() => {
      if (activeQuery !== null) { // If activeQuery is '' (for all users) or a string (for filtering)
        fetchTaggableUsers(activeQuery);
      } else { // activeQuery is null, so hide suggestions
        setSuggestions([]);
        setShowSuggestions(false);
      }
    }, 300); // 300ms debounce

    return () => clearTimeout(handler);
  }, [activeQuery, fetchTaggableUsers]);

  const handleInputChange = (event) => {
    const newValue = event.target.value;
    setInputValue(newValue);
    onChange(newValue); // Propagate raw text change to parent

    const cursorPos = event.target.selectionStart;
    const textBeforeCursor = newValue.substring(0, cursorPos);
    const lastAtSymbolIndex = textBeforeCursor.lastIndexOf('@');

    if (lastAtSymbolIndex !== -1) {
      // Extract the potential query string from '@' to cursor
      const potentialQuery = textBeforeCursor.substring(lastAtSymbolIndex + 1);
      
      // A valid query for a username part should not contain spaces.
      // If potentialQuery is empty, it means the cursor is right after '@'.
      if (!/\s/.test(potentialQuery)) { 
        setActiveQuery(potentialQuery); // This will be '' if cursor is right after @, triggering fetch for all
        setShowSuggestions(true); // Show suggestions container immediately when @ is typed
      } else {
        // A space was typed after '@' in the current query part, so it's no longer a valid mention query
        setActiveQuery(null); 
        setShowSuggestions(false);
      }
    } else {
      // No '@' found in a position to start a mention query
      setActiveQuery(null);
      setShowSuggestions(false);
    }
  };

  const handleSuggestionClick = (userToMention) => {
    const currentText = inputValue;
    const cursorPos = textareaRef.current.selectionStart;
    
    let startIndex = -1;
    const textBeforeCursor = currentText.substring(0, cursorPos);
    const lastAtSymbolIndex = textBeforeCursor.lastIndexOf('@');

    if (lastAtSymbolIndex !== -1) {
        const currentQueryPart = textBeforeCursor.substring(lastAtSymbolIndex + 1);
        // Check if the text from the last '@' to the cursor matches the active query
        // This handles cases where activeQuery is '' (cursor right after '@')
        // or activeQuery is some text (e.g., 'john')
        if (activeQuery === currentQueryPart) {
             startIndex = lastAtSymbolIndex;
        } else {
            // Fallback: if activeQuery and current text state are desynced,
            // try to find the @ symbol that started the query.
            // This might happen if the user moves the cursor after typing @.
            // We'll replace from the last '@' up to the current cursor.
            startIndex = lastAtSymbolIndex;
        }
    }


    let newText;
    if (startIndex !== -1) {
        const textBefore = currentText.substring(0, startIndex);
        // The part to replace is from startIndex up to the current cursor position.
        const textAfter = currentText.substring(cursorPos);
        newText = `${textBefore}@${userToMention.username} ${textAfter}`;
    } else {
        // Fallback: if we can't find the exact query start, append (should be rare)
        // Or if the user typed @ somewhere else and then clicked a suggestion without a valid active query.
        newText = `${currentText}${currentText.endsWith(' ') || currentText.length === 0 ? '' : ' '}@${userToMention.username} `;
    }
    
    setInputValue(newText);
    onChange(newText);

    onMentionsChange(prevMentions => {
      const existingMention = prevMentions.find(m => m.id === userToMention.id);
      if (existingMention) return prevMentions; // Avoid duplicates
      return [...prevMentions, userToMention];
    });

    setShowSuggestions(false);
    setActiveQuery(null); // Reset active query after selection
    
    setTimeout(() => {
        if (textareaRef.current) {
            textareaRef.current.focus();
            // Position cursor after the inserted mention + space
            const cursorPosition = newText.lastIndexOf(`@${userToMention.username} `) + `@${userToMention.username} `.length;
            if (cursorPosition >=0 && cursorPosition <= newText.length) {
                 textareaRef.current.setSelectionRange(cursorPosition, cursorPosition);
            }
        }
    }, 0);
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (suggestionsRef.current && !suggestionsRef.current.contains(event.target) &&
          textareaRef.current && !textareaRef.current.contains(event.target)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div style={{ position: 'relative' }} className={className || ''}>
      <textarea
        ref={textareaRef}
        value={inputValue}
        onChange={handleInputChange}
        placeholder={placeholder}
        rows="2" // As per your attachment, changed from 3
        style={{ width: '100%', boxSizing: 'border-box', padding: '8px', resize: 'none' }}
      />
      {showSuggestions && ( // Show suggestions container if showSuggestions is true
        <ul
          ref={suggestionsRef}
          style={{
            position: 'absolute',
            top: textareaRef.current ? `${textareaRef.current.offsetHeight}px` : '100%',
            left: 0,
            width: '100%',
            backgroundColor: 'white',
            border: '1px solid #ccc',
            borderRadius: '0 0 4px 4px',
            listStyleType: 'none',
            padding: 0,
            margin: 0,
            maxHeight: '150px',
            overflowY: 'auto',
            zIndex: 1000,
            boxSizing: 'border-box'
          }}
        >
          {suggestions.length > 0 ? (
            suggestions.map(user => (
              <li
                key={user.id}
                onClick={() => handleSuggestionClick(user)}
                style={{
                  padding: '8px 12px',
                  cursor: 'pointer',
                  borderBottom: '1px solid #eee',
                  display: 'flex',
                  alignItems: 'center'
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f0f0f0'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'white'}
              >
                <img 
                  src={constructMediaUrl(user.profile_image)} 
                  alt={user.name} 
                  style={{width: '24px', height: '24px', borderRadius: '50%', marginRight: '8px'}}
                  onError={(e) => e.target.src = '/assets/images/default-avatar.png'}
                />
                {user.name} <span style={{color: '#555', marginLeft: '4px'}}>@{user.username}</span>
              </li>
            ))
          ) : (
            // Show "No users found" only if an active query was made (i.e., activeQuery is not null)
            // and suggestions array is empty.
            activeQuery !== null && <li style={{padding: '8px 12px', color: '#777'}}>No users found.</li>
          )}
        </ul>
      )}
    </div>
  );
};

export default MentionInput;