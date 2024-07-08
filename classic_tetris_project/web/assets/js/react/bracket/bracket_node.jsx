import React from 'react';

const WINNER_COLOR = "#f5cf00";

const BracketNode = (props) => {
  const { label, url, left, right, depth, color, parentColor, isRoot = false } = props;

  const showChildren = (depth === null || depth > 0)
  const childDepth = depth === null ? null : depth - 1;

  const matchColor = color || parentColor;

  const renderLeftChild = () => {
    if (left.child) {
      return (
        <div className="bracket-match-left">
          <BracketNode {...left.child} depth={childDepth} parentColor={matchColor} />
        </div>
      );
    } else {
      return (
        <div className="bracket-match-left">
          <div className="bracket-spacer"></div>
        </div>
      )
    }
  };

  const renderRightChild = () => {
    if (right.child) {
      return (
        <div className="bracket-match-right">
          <BracketNode {...right.child} depth={childDepth} parentColor={matchColor} />
        </div>
      );
    } else {
      return (
        <div className="bracket-match-right">
          <div className="bracket-spacer"></div>
        </div>
      )
    }
  };

  const renderPaths = () => {
    if (left.child && right.child) {
      return (
        <>
          <div className="bracket-path-left"></div>
          <div className="bracket-path-right"></div>
        </>
      );
    } else if (left.child) {
      return (
        <div className="bracket-path-top"></div>
      )
    } else if (right.child) {
      return (
        <div className="bracket-path-bottom"></div>
      )
    }
  };

  const renderPlayerNode = (node) => {
    const { playerName, playerSeed, url, winner, child } = node;
    let playerColor = color || child?.color || matchColor;
    if (isRoot && winner) {
      playerColor = WINNER_COLOR;
    }

    return (
      <div className={"bracket-match-player"} style={playerColor && { background: playerColor }}>
        {playerSeed &&
        <div className="player-seed">{playerSeed}</div>
        }
        <div className="player-name">
          {url
            ? <a href={url}>{playerName}</a>
            : playerName
          }
        </div>
      </div>
    )
  }

  return (
    <div className="bracket-match-container">
      {(left.child || right.child) && showChildren &&
      <>
        {renderLeftChild()}
        {renderRightChild()}
      </>
      }

      {showChildren && renderPaths()}

      <div className="bracket-match">
        {label &&
        <div className="bracket-match-number">
          {url
            ? <a href={url}>{label}</a>
            : label
          }
        </div>
        }
        {renderPlayerNode(left)}
        {renderPlayerNode(right)}
      </div>
      
    </div>
  );
};


export default BracketNode;
