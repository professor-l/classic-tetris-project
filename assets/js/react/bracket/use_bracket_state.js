import { useReducer } from 'react';

const DEFAULTS = {
  scaled: true,
  fitToWindow: false,
  width: null,
  height: null,
  depth: null,
  root: null,
  showBorder: false,
  autoRefresh: true,
  embed: false,
};

const _parseInt = (value, field) => {
  const parsed = parseInt(value);
  if (isNaN(parsed)) {
    return DEFAULTS[field];
  } else {
    return parsed;
  }
};

const _parseBool = (value, field) => {
  if (value === true || value === 'true') {
    return true;
  } else if (value === false || value === 'false') {
    return false;
  } else {
    return DEFAULTS[field];
  }
};


const initialState = (props) => {
  return {
    scaled: _parseBool(props.scaled, 'scaled'),
    fitToWindow: _parseBool(props.fitToWindow, 'fitToWindow'),
    width: _parseInt(props.width, 'width'),
    height: _parseInt(props.height, 'height'),
    depth: _parseInt(props.depth, 'depth'),
    root: _parseInt(props.root, 'root'),
    showBorder: _parseBool(props.showBorder, 'showBorder'),
    autoRefresh: _parseBool(props.autoRefresh, 'autoRefresh'),
    embed: _parseBool(props.embed, 'embed'),
  }
};

const bracketReducer = (state, action) => {
  switch (action.type) {
    case 'SET_INT':
      return { ...state, [action.field]: _parseInt(action.value, action.field) };
    case 'SET_BOOL':
      return { ...state, [action.field]: _parseBool(action.value, action.field) };
  }
};

export const getBracketUrl = (baseUrl, state) => {
  const url = new URL(baseUrl);
  Object.entries(state).forEach(([ field, value ], _) => {
    if (field in DEFAULTS && value !== DEFAULTS[field]) {
      url.searchParams.set(field, value);
    }
  });
  return url.href;
};

const useBracketState = (props) => {
  const [state, dispatch] = useReducer(bracketReducer, props, initialState);

  return { state, dispatch };
};


export default useBracketState;
