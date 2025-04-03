import { Box, Text } from '@chakra-ui/react';
import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

const MotionBox = motion(Box);

const BotJapanese = () => {
  const [message, setMessage] = useState('');

  useEffect(() => {
    const checkFile = async () => {
      try {
        const response = await fetch('/japanese.txt');
        const text = await response.text();
        setMessage(text);
      } catch (error) {
        console.error('Error reading Japanese response:', error);
      }
    };

    const interval = setInterval(checkFile, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <MotionBox
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ 
        duration: 0.5,
        ease: "linear",
        opacity: { duration: 0.2 }
      }}
      p={4}
      borderRadius="lg"
      bg="rgba(173, 216, 230, 0.7)"
      backdropFilter="blur(10px)"
      boxShadow="lg"
      maxW="600px"
      m={4}
    >
      <Text
        fontSize="xl"
        color="blue.800"
        fontWeight="bold"
        fontFamily="'Hiragino Kaku Gothic Pro', sans-serif"
      >
        {message}
      </Text>
    </MotionBox>
  );
};

export default BotJapanese;
