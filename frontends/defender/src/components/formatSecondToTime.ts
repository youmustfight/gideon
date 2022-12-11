export const formatSecondToTime = (number: number) => `${Math.floor((number ?? 0) / 60)}:${number % 60}`;
