import React, { useEffect, useCallback, useRef, useMemo } from 'react';
import PropTypes from 'prop-types';

import BracketNode from './bracket_node';


const findMatch = (matches, root) => {
  if (!matches) {
    return null;
  } else if (root === null) {
    return matches;
  } else if (matches.matchNumber === root) {
    return matches;
  } else {
    return findMatch(matches.left.child, root) || findMatch(matches.right.child, root);
  }
};

const TournamentBracket = (props) => {
  const { matches, scaled, fitToWindow, width, height, depth, root, showBorder, customBracketColor } = props;

  const containerRef = useRef(null);
  const bracketRef = useRef(null);

  const rootNode = useMemo(() => findMatch(matches, root),
    [matches, root]);

  const resize = useCallback(() => {
    const flexibleHeight = !height && !fitToWindow;

    if (fitToWindow) {
      containerRef.current.style.height = 'vh';
    } else if (!height) {
      containerRef.current.style.height = null;
    }
    if (!scaled) {
      bracketRef.current.style.transform = null;
    }

    if (scaled) {
      const outerWidth = containerRef.current.offsetWidth;
      const innerWidth = bracketRef.current.offsetWidth;
      const outerHeight = (flexibleHeight ? Infinity : containerRef.current.offsetHeight);
      const innerHeight = bracketRef.current.offsetHeight;
      const scale = Math.min(outerWidth / innerWidth, outerHeight / innerHeight);
      bracketRef.current.style.transform = `scale(${scale})`;

      if (flexibleHeight) {
        const scaledHeight = bracketRef.current.getBoundingClientRect().height;
        containerRef.current.style.height = `${scaledHeight}px`;
      }
    }
  });

  useEffect(resize);
  useEffect(() => {
    window.addEventListener('resize', resize);
    return () => { window.removeEventListener('resize', resize); };
  }, [scaled, fitToWindow, height]);

  return (
    <div className={'bracket-container' + (showBorder ? ' bracket-container--border' : '') + (scaled ? ' bracket-container--scaled' : '')}
      ref={containerRef}
      style={{
        width: (fitToWindow ? '100%' : (width ? `${width}px` : null)),
        height: (fitToWindow ? '100vh' : (height ? `${height}px` : null)),
      }}>
      <div className="bracket" ref={bracketRef}>
        {rootNode && <BracketNode {...rootNode} depth={depth} customBracketColor={customBracketColor} />}
      </div>
    </div>
  );
};
TournamentBracket.propTypes = {
  matches: PropTypes.object.isRequired,
  scaled: PropTypes.bool,
  width: PropTypes.number,
  height: PropTypes.number,
  depth: PropTypes.number,
  root: PropTypes.number,
  showBorder: PropTypes.bool,
  autoRefresh: PropTypes.bool,
  customBracketColor: PropTypes.string,
};
TournamentBracket.defaultProps = {
  scaled: true,
  width: null,
  height: null,
  depth: null,
  root: null,
  showBorder: false,
  autoRefresh: true,
  customBracketColor: null,
};


export default TournamentBracket;
