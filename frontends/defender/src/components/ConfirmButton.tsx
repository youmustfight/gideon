import React, { useEffect, useState } from "react";
import { Button } from "./styled/common/Button";

type TConfirmButtonProps = {
  disabled?: boolean;
  prompts: string[];
  onClick: Function;
  style?: any;
};

export const ConfirmButton: React.FC<TConfirmButtonProps> = ({ disabled, prompts, onClick, style }) => {
  const [promptPosition, setPromptPosition] = useState(0);
  // If we don't confirm deletion after X time, reset prompt
  useEffect(() => {
    const tid = setTimeout(() => {
      if (promptPosition !== 0) setPromptPosition(0);
    }, 1000 * 5);
    return () => clearInterval(tid);
  }, [promptPosition]);

  // RENDER
  return (
    <Button
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
    </Button>
  );
};
