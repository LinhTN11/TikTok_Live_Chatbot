import { Box, Text } from '@chakra-ui/react';
import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

const MotionBox = motion(Box);

const UserChat = () => {
  const [message, setMessage] = useState('');

  useEffect(() => {
    const checkFile = async () => {
      try {
        const response = await fetch('/chat.txt');
        const text = await response.text();
        setMessage(text);
      } catch (error) {
        console.error('Error reading chat:', error);
      }
    };

    const interval = setInterval(checkFile, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <MotionBox
      initial={{ opacity: 0, x: 50 }} // Changed from -50 to 50 for right-to-left
      animate={{ 
        opacity: 1, 
        x: 0,
        rotate: [0, -2, 2, -2, 0] // Shake animation
      }}
      transition={{ 
        duration: 0.5,
        ease: "linear",
        opacity: { duration: 0.2 },
        rotate: { duration: 0.5, ease: "easeInOut" }
      }}
      p={4}
      borderRadius="lg"
      bg="rgba(87, 39, 33, 0.8)" // Hu Tao's dark brown background
      backdropFilter="blur(10px)"
      boxShadow="lg"
      maxW="600px"
      w="fit-content"
      m={4}
      display="inline-block"
      position="relative"
      border="6px solid" // Changed from 2px to 4px
      borderColor="#d98c7c" // Darker brown border
    >
      <Text
        fontSize="xl"
        color="white" // Changed to white text
        fontWeight="bold"
        fontFamily="'Be Vietnam Pro', 'Segoe UI', 'Roboto', system-ui, sans-serif"
        letterSpacing="0.5px"
        whiteSpace="pre-wrap"
        wordBreak="break-word"
      >
        {message}
      </Text>
    </MotionBox>
  );
};

export default UserChat;
