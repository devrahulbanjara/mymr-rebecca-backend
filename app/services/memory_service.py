from collections import deque


class MemoryService:
    """
    Manages conversation history in memory.
    Each patient has their own conversation history (max 6 exchanges = 12 messages).
    """

    def __init__(self, max_exchanges: int = 6):
        """
        Initialize the memory service.
        
        Args:
            max_exchanges: Maximum number of exchanges (user + assistant pairs) to keep
        """
        # Dictionary to store chat history per patient
        # Key: patient_id, Value: deque of messages
        self._conversations: dict[str, deque] = {}
        self.max_exchanges = max_exchanges
        self.max_messages = max_exchanges * 2  # Each exchange = user + assistant message

    def add_message(self, patient_id: str, role: str, content: str) -> None:
        """
        Add a message to the patient's conversation history.
        
        Args:
            patient_id: UUID of the patient
            role: Either "user" or "assistant"
            content: The message content
        """
        if patient_id not in self._conversations:
            self._conversations[patient_id] = deque(maxlen=self.max_messages)
        
        message = {
            "role": role,
            "content": content
        }
        
        self._conversations[patient_id].append(message)

    def get_conversation_history(self, patient_id: str) -> list[dict[str, str]]:
        """
        Retrieve conversation history for a patient.
        
        Args:
            patient_id: UUID of the patient
            
        Returns:
            List of message dictionaries with role and content
        """
        if patient_id not in self._conversations:
            return []
        
        return list(self._conversations[patient_id])

    def get_formatted_history(self, patient_id: str) -> str:
        """
        Get conversation history formatted as a string for context.
        
        Args:
            patient_id: UUID of the patient
            
        Returns:
            Formatted conversation history string
        """
        history = self.get_conversation_history(patient_id)
        
        if not history:
            return ""
        
        formatted = "CONVERSATION HISTORY:\n"
        for msg in history:
            role = msg["role"].upper()
            content = msg["content"]
            formatted += f"{role}: {content}\n\n"
        
        return formatted

    def clear_conversation_history(self, patient_id: str) -> bool:
        """
        Clear conversation history for a specific patient.
        
        Args:
            patient_id: UUID of the patient
            
        Returns:
            True if successful
        """
        try:
            if patient_id in self._conversations:
                del self._conversations[patient_id]
            return True
        except Exception as e:
            print(f"Error clearing conversation history: {e}")
            return False

    def get_message_count(self, patient_id: str) -> int:
        """
        Get the number of messages in a patient's conversation history.
        
        Args:
            patient_id: UUID of the patient
            
        Returns:
            Number of messages
        """
        if patient_id not in self._conversations:
            return 0
        
        return len(self._conversations[patient_id])

    def get_exchange_count(self, patient_id: str) -> int:
        """
        Get the number of exchanges (user + assistant pairs) in history.
        
        Args:
            patient_id: UUID of the patient
            
        Returns:
            Number of exchanges
        """
        return self.get_message_count(patient_id) // 2

    def has_history(self, patient_id: str) -> bool:
        """
        Check if a patient has any conversation history.
        
        Args:
            patient_id: UUID of the patient
            
        Returns:
            True if history exists
        """
        return patient_id in self._conversations and len(self._conversations[patient_id]) > 0

    def get_all_patient_ids(self) -> list[str]:
        """
        Get all patient IDs with conversation history.
        
        Returns:
            List of patient IDs
        """
        return list(self._conversations.keys())

    def clear_all_histories(self) -> bool:
        """
        Clear all conversation histories.
        
        Returns:
            True if successful
        """
        try:
            self._conversations.clear()
            return True
        except Exception as e:
            print(f"Error clearing all histories: {e}")
            return False

    def get_stats(self) -> dict[str, any]:
        """
        Get statistics about stored conversations.
        
        Returns:
            Dictionary with statistics
        """
        return {
            "total_patients": len(self._conversations),
            "max_exchanges_per_patient": self.max_exchanges,
            "max_messages_per_patient": self.max_messages,
            "patient_message_counts": {
                patient_id: len(messages)
                for patient_id, messages in self._conversations.items()
            }
        }
