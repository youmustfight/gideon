import { createGlobalStyle } from "styled-components";
// import GTWalsheimBold from '../assets/fonts/GT-Walsheim-Bold';

export const GlobalCSS = createGlobalStyle`
  :root {
    --color-font: #001ecd;
    --color-bg: #fafaff;
  }

  * {
    box-sizing: border-box;
  }

  a {
    font-family: inherit;
    &:visited, &:hover, &:active {
      color: inherit;
    }
  }
  
  @font-face {
    font-family: 'GT Walsheim';
    font-style: normal;
    src: url('./fonts/GT-Walsheim-Ultra-Light.woff2') format('woff2');
    font-weight: 100;
  }
  @font-face {
    font-family: 'GT Walsheim';
    font-style: normal;
    src: url('./fonts/GT-Walsheim-Thin.woff2') format('woff2');
    font-weight: 200;
  }
  @font-face {
    font-family: 'GT Walsheim';
    font-style: normal;
    src: url('./fonts/GT-Walsheim-Light.woff2') format('woff2');
    font-weight: 300;
  }
  @font-face {
    font-family: 'GT Walsheim';
    font-style: normal;
    src: url('./fonts/GT-Walsheim-Regular.woff2') format('woff2');
    font-weight: 500;
  }
  @font-face {
    font-family: 'GT Walsheim';
    font-style: normal;
    src: url('./fonts/GT-Walsheim-Medium.woff2') format('woff2');
    font-weight: 600;
  }
  @font-face {
    font-family: 'GT Walsheim';
    font-style: normal;
    src: url('./fonts/GT-Walsheim-Bold.woff2') format('woff2');
    font-weight: 700;
  }
  @font-face {
    font-family: 'GT Walsheim';
    font-style: normal;
    src: url('./fonts/GT-Walsheim-Black.woff2') format('woff2');
    font-weight: 800;
  }
  @font-face {
    font-family: 'GT Walsheim';
    font-style: normal;
    src: url('./fonts/GT-Walsheim-Ultra-Bold.woff2') format('woff2');
    font-weight: 900;
  }
`;
