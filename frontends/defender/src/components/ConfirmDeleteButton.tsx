import React, { useEffect, useState } from "react";

type TConfirmDeleteButtonProps = {
  disabled?: boolean;
  prompts: string[];
  onClick: Function;
  style?: any;
};

export const ConfirmDeleteButton: React.FC<TConfirmDeleteButtonProps> = ({ disabled, prompts, onClick, style }) => {
  const [promptPosition, setPromptPosition] = useState(0);
  // If we don't confirm deletion after X time, reset prompt
  useEffect(() => {
    setTimeout(() => {
      if (promptPosition !== 0) setPromptPosition(0);
    }, 1000 * 5);
  }, [promptPosition]);

  // RENDER
  return (
    <button
      disabled={disabled}
      onClick={() => {
        if (promptPosition === prompts.length - 1) {
          onClick();
        } else {
          setPromptPosition(promptPosition + 1);
        }
      }}
      style={style}
    >
      {prompts[promptPosition]}
    </button>
  );
};
