import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ChakraProvider, extendTheme } from '@chakra-ui/react';
import UserChat from './routes/UserChat';
import BotJapanese from './routes/BotJapanese';
import BotVietnamese from './routes/BotVietnamese';

const theme = extendTheme({
  styles: {
    global: {
      body: {
        bg: 'transparent',
      },
    },
  },
});

function App() {
  return (
    <ChakraProvider theme={theme}>
      <BrowserRouter>
        <Routes>
          <Route path="/user" element={<UserChat />} />
          <Route path="/japanese" element={<BotJapanese />} />
          <Route path="/vietnamese" element={<BotVietnamese />} />
        </Routes>
      </BrowserRouter>
    </ChakraProvider>
  );
}

export default App;
