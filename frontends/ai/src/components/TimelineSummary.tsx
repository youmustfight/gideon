import axios from "axios";
import React, { useState } from "react";
import { Link, useMatch } from "react-router-dom";
import styled from "styled-components";
import { TDocument, useDocuments } from "../data/useDocuments";
import { getGideonApiUrl } from "../env";

export const TimelineSummary = () => {
  const [events, setEvents] = useState([]);
  const [isLoadingTimeline, setIsLoadingTimeline] = useState(false);
  const generateTimeline = (e) => {
    e.preventDefault();
    setEvents([]);
    setIsLoadingTimeline(true);
    return axios
      .post(`${getGideonApiUrl()}/v1/timeline`)
      .then((res) => {
        setEvents(res.data.events);
        setIsLoadingTimeline(false);
      });
  };

  // RENDER
  return (
    <StyledTimelineSummary>
        {events.length > 0 && (
          <>
            {events.map((event) => <p>{event}</p>)}
            <br />
          </>
        )}
        {isLoadingTimeline ? (
          <h2>Loading...</h2>
        ) : (
          <button className='generate-timeline-btn' onClick={generateTimeline}>
            Generate Timeline
          </button>
        )}
    </StyledTimelineSummary>
  );
};

const StyledTimelineSummary = styled.div`
  p {
    font-size: 14px;
    margin: 0;
    margin-top: 4px;
  }
  small {
    margin: 4px 0;
    font-size: 12px;
  }
  & > ul {
    padding-left: 0 !important;
    list-style-type: none !important;
  }
  li {
    margin: 4px 0;
    & > div {
      padding: 4px;
    }
  }
`;
