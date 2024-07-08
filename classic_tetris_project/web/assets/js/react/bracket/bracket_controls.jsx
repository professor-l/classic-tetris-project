import React from 'react';

import { getBracketUrl } from './use_bracket_state';


const BracketControls = (props) => {
  const { baseUrl, state, dispatch } = props;

  const bracketUrl = getBracketUrl(baseUrl, state);
  const embedUrl = getBracketUrl(baseUrl, { ...state, embed: true });

  return (
    <div className="bracket-controls">
      <label>
        Scaled:
        <input type="checkbox" defaultChecked={state.scaled} onChange={e => dispatch({ type: 'SET_BOOL', field: 'scaled', value: e.target.checked })}/>
      </label>
      <label>
        Fit to Window:
        <input type="checkbox" defaultChecked={state.fitToWindow} onChange={e => dispatch({ type: 'SET_BOOL', field: 'fitToWindow', value: e.target.checked })}/>
      </label>
      <label>
        Width:
        <input type="text" defaultValue={state.width} onChange={e => dispatch({ type: 'SET_INT', field: 'width', value: e.target.value })}/>
      </label>
      <label>
        Height:
        <input type="text" defaultValue={state.height} onChange={e => dispatch({ type: 'SET_INT', field: 'height', value: e.target.value })}/>
      </label>
      <label>
        Bracket Depth:
        <input type="text" defaultValue={state.depth} onChange={e => dispatch({ type: 'SET_INT', field: 'depth', value: e.target.value })}/>
      </label>
      <label>
        Root Match #:
        <input type="text" defaultValue={state.root} onChange={e => dispatch({ type: 'SET_INT', field: 'root', value: e.target.value })}/>
      </label>
      <label>
        Show Border:
        <input type="checkbox" defaultChecked={state.showBorder} onChange={e => dispatch({ type: 'SET_BOOL', field: 'showBorder', value: e.target.checked })}/>
      </label>
      <label>
        Two sided (facing in):
        <input type="checkbox" defaultChecked={state.twoSided} onChange={e => dispatch({ type: 'SET_BOOL', field: 'twoSided', value: e.target.checked })}/>
      </label>
      <label>
        Show Match Numbers:
        <input type="checkbox" defaultChecked={state.showMatchNumbers} onChange={e => dispatch({ type: 'SET_BOOL', field: 'showMatchNumbers', value: e.target.checked })}/>
      </label>
      <label>
        Refresh Every Minute:
        <input type="checkbox" defaultChecked={state.autoRefresh} onChange={e => dispatch({ type: 'SET_BOOL', field: 'autoRefresh', value: e.target.checked })}/>
      </label>
      <div>
        Link to current state:<br/>
        <a href={bracketUrl}>{bracketUrl}</a>
      </div>
      <div>
        Embed URL:<br/>
        <a href={embedUrl}>{embedUrl}</a>
      </div>
    </div>
  );
}


export default BracketControls;
