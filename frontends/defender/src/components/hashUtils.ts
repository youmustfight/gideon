export const formatHashForSentenceHighlight = (sentence_start?: number | string, sentence_end?: number | string) => {
  if (sentence_start && sentence_end) {
    return `S${sentence_start}-S${sentence_end}`;
  }
  if (sentence_start) {
    return `S${sentence_start}`;
  }
  return "";
};

export const getHashHighlightingSentenceStart = (hash: string) => {
  const sentenceHashSegments = (hash ?? "").replace("#", "").split("-");
  return sentenceHashSegments[0];
};

export const isHashHighlightingSentence = (hash: string, sentenceNumToCheck: number | string) => {
  const sentenceNum = Number(sentenceNumToCheck);
  const sentenceHashSegments = (hash ?? "").replace("#", "").split("-");
  const sentenceStartNum = sentenceHashSegments[0]?.replace("S", "");
  const sentenceEndNum = sentenceHashSegments[1]?.replace("S", "");
  // if only sentence start exists, it's a single selection
  if (sentenceStartNum && !sentenceEndNum) {
    return sentenceNum === Number(sentenceStartNum);
  }
  // if its both
  if (sentenceStartNum && sentenceEndNum) {
    return sentenceNum >= Number(sentenceStartNum) && sentenceNum <= Number(sentenceEndNum);
  }
  // otherwise ?
  return false;
};
