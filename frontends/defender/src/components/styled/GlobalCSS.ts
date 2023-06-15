import { createGlobalStyle } from "styled-components";
// import GTWalsheimBold from '../assets/fonts/GT-Walsheim-Bold';

export const GlobalCSS = createGlobalStyle`
  :root {
    --color-black-200: #333355;
    --color-black-500: #8f8fa4;
    --color-black-700: #babacb;
    --color-black-800: #eaeffa;
    --color-black-900: #fafaff;
    --color-green-500: #3c7a3f;
    --color-green-900: #fafffa;
    --color-blue-500: #001ecd;
    --color-blue-700: #97a2de;
    --color-blue-800: #bdc7ff;
    --color-blue-850: #f5f5fa;
    --color-blue-900: #fafaff;

    --effects-box-shadow-500: rgb(50 50 223 / 15%) 0px 50px 100px -20px, rgb(0 0 0 / 10%) 0px 30px 60px -30px; 
  }

  * {
    box-sizing: border-box;
    font-family: sans-serif;
  }

  a {
    font-family: inherit;
    &:visited, &:hover, &:active {
      color: inherit;
    }
  }

  // SERIF
  @font-face {
    font-family: 'Zodiak';
    src: url('./fonts/Zodiak-Regular.woff2') format('woff2');
    font-weight: 400;
  }
  @font-face {
    font-family: 'Zodiak';
    src: url('./fonts/Zodiak-Bold.woff2') format('woff2');
    font-weight: 700;
  }
  @font-face {
    font-family: 'Zodiak';
    src: url('./fonts/Zodiak-Extrabold.woff2') format('woff2');
    font-weight: 800;
  }
  @font-face {
    font-family: 'Zodiak';
    src: url('./fonts/Zodiak-Black.woff2') format('woff2');
    font-weight: 900;
  }
  
  // SAN-SERIF
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
