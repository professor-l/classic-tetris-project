import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

import useBracketState from './use_bracket_state';
import TournamentBracket from './tournament_bracket';
import BracketControls from './bracket_controls';


export const COMPONENT_NAME = 'TournamentBracketController';

const TournamentBracketController = (props) => {
  const { bracketUrl, refreshUrl } = props;
  const { state, dispatch } = useBracketState(props);

  const [matches, setMatches] = useState(props.matches);
  const [timestamp, setTimestamp] = useState(props.ts);

  useEffect(() => {
    let id = null;
    if (state.autoRefresh) {
      id = window.setInterval(() => {
        const url = new URL(refreshUrl);
        url.searchParams.set('ts', timestamp);
        fetch(url.href)
          .then(response => response.json())
          .then(data => {
            if (data['matches']) {
              setMatches(data.matches);
              setTimestamp(data.ts);
            }
          });
      }, 60000);
    }

    return () => {
      if (id !== null) {
        window.clearInterval(id);
      }
    };
  }, [state.autoRefresh, timestamp]);

  return (
    <div>
      <TournamentBracket matches={matches} {...state}/>
      {!state.embed &&
      <BracketControls baseUrl={bracketUrl} state={state} dispatch={dispatch}/>
      }
    </div>
  );
};


export default TournamentBracketController;
