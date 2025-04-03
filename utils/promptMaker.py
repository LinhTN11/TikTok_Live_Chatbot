import json
import sys

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

outputNum = 20

def getIdentity(identityPath):  
    with open(identityPath, "r", encoding="utf-8") as f:
        identityContext = f.read()
    return {"role": "user", "content": identityContext}
    
def getPrompt():
    prompt = []
    prompt.append(getIdentity("characterConfig/Shiro/identity_vi.txt"))
    prompt.append({
        "role": "system",
        "content": """NGUYÊN TẮC TRẢ LỜI:
        1. Luôn TRẢ LỜI ĐÚNG chủ đề của câu hỏi
        2. KHÔNG lan man sang chủ đề khác
        3. Giữ tính cách tsundere nhưng phải trả lời có nội dung
        4. Trả lời bằng tiếng Việt, chỉ dùng một số từ tiếng Nhật cơ bản
        5. Giới hạn trong 15-20 từ và phải liên quan đến câu hỏi

        VÍ DỤ:
        - Khi được hỏi về anime: "H-hmph! Dĩ nhiên tôi biết anime đó... là một trong những anime hay nhất đấy!"
        - Khi được hỏi về game: "Baka! Tôi đã phá đảo game đó từ lâu rồi..."
        - Khi được khen: "Đ-đừng khen như thế... mà cảm ơn nhé..."
        
        TUYỆT ĐỐI KHÔNG:
        - Trả lời lạc đề
        - Nói về chủ đề không được hỏi
        - Bỏ qua nội dung câu hỏi
        """
    })
    
    # Thêm lịch sử hội thoại
    with open("conversation.json", "r") as f:
        data = json.load(f)
    history = data["history"]
    
    # Nhấn mạnh yêu cầu trả lời đúng trọng tâm
    prompt.append({
        "role": "system",
        "content": "Hãy trả lời ĐÚNG nội dung tin nhắn sau, KHÔNG LẠC ĐỀ:"
    })
    prompt.append(history[-1])
    
    return prompt

if __name__ == "__main__":
    prompt = getPrompt()
    print(prompt)
    print(len(prompt))