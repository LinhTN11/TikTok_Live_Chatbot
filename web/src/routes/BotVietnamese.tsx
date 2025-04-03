import { Box, Text } from '@chakra-ui/react';
import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

const MotionBox = motion(Box);

const BotVietnamese = () => {
  const [message, setMessage] = useState('');

  useEffect(() => {
    const checkFile = async () => {
      try {
        const response = await fetch('/output.txt');
        const text = await response.text();
        setMessage(text);
      } catch (error) {
        console.error('Error reading Vietnamese response:', error);
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
      bg="rgba(144, 238, 144, 0.7)"
      backdropFilter="blur(10px)"
      boxShadow="lg"
      maxW="600px"
      m={4}
    >
      <Text
        fontSize="xl"
        color="green.800"
        fontWeight="bold"
        fontFamily="'Be Vietnam Pro', 'Segoe UI', 'Roboto', system-ui, sans-serif"
        letterSpacing="0.5px"
      >
        {message}
      </Text>
    </MotionBox>
  );
};

export default BotVietnamese;
