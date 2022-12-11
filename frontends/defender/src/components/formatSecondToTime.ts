export const formatSecondToTime = (number: number) =>
  `${Math.floor((number ?? 0) / 60)}:${String(number % 60).padStart(2, 0)}`;
