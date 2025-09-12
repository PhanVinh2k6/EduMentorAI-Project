import streamlit as st
import json
import sqlite3
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List, Optional
import requests
import base64
from io import BytesIO
from PIL import Image

# Configure Streamlit page
st.set_page_config(
    page_title="EduMentor AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

class DatabaseManager:
    """Manages SQLite database operations"""
    
    def __init__(self, db_name: str = "edumentor.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Lessons table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                subject TEXT,
                content TEXT,
                outline TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Student progress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT,
                lesson_id INTEGER,
                quiz_score INTEGER,
                completion_status TEXT,
                study_time INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lesson_id) REFERENCES lessons (id)
            )
        ''')
        
        # Generated images table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS generated_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lesson_id INTEGER,
                prompt TEXT,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lesson_id) REFERENCES lessons (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_lesson(self, title: str, subject: str, content: str, outline: str) -> int:
        """Save a new lesson to database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO lessons (title, subject, content, outline)
            VALUES (?, ?, ?, ?)
        ''', (title, subject, content, outline))
        lesson_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return lesson_id
    
    def get_lessons(self) -> List[Dict]:
        """Retrieve all lessons"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lessons ORDER BY created_at DESC')
        lessons = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': lesson[0],
                'title': lesson[1],
                'subject': lesson[2],
                'content': lesson[3],
                'outline': lesson[4],
                'created_at': lesson[5]
            }
            for lesson in lessons
        ]
    
    def save_progress(self, student_name: str, lesson_id: int, quiz_score: int, 
                     completion_status: str, study_time: int):
        """Save student progress"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO student_progress 
            (student_name, lesson_id, quiz_score, completion_status, study_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (student_name, lesson_id, quiz_score, completion_status, study_time))
        conn.commit()
        conn.close()

class ContentGenerator:
    """Handles AI content generation using DeepSeek API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"
    
    def generate_lesson_outline(self, topic: str, subject: str, grade_level: str = "Trung học") -> Dict:
        """Generate lesson outline using DeepSeek API"""
        if not self.api_key:
            # Fallback template for demonstration
            return {
                "title": f"Bài học về {topic}",
                "outline": [
                    "1. Giới thiệu và mục tiêu học tập",
                    "2. Kiến thức cơ bản",
                    "3. Ví dụ minh họa",
                    "4. Bài tập thực hành",
                    "5. Tổng kết và đánh giá"
                ],
                "content": f"Nội dung chi tiết về {topic} trong môn {subject}...",
                "key_points": [
                    f"Khái niệm cơ bản về {topic}",
                    f"Ứng dụng thực tế của {topic}",
                    f"Các bài tập liên quan đến {topic}"
                ],
                "estimated_time": "45 phút"
            }
        
        # TODO: Implement actual DeepSeek API call
        prompt = f"""
        Tạo dàn ý bài giảng chi tiết cho chủ đề: {topic}
        Môn học: {subject}
        Cấp độ: {grade_level}
        
        Yêu cầu:
        1. Dàn ý rõ ràng, logic
        2. Nội dung phù hợp với cấp độ học sinh
        3. Bao gồm hoạt động thực hành
        4. Thời gian dự kiến cho mỗi phần
        """
        
        return self.generate_lesson_outline(topic, subject, grade_level)
    
    def generate_quiz_questions(self, topic: str, num_questions: int = 5) -> List[Dict]:
        """Generate quiz questions based on topic"""
        # Sample quiz generation - replace with actual AI generation
        questions = []
        for i in range(num_questions):
            questions.append({
                "question": f"Câu hỏi {i+1} về {topic}?",
                "options": ["Đáp án A", "Đáp án B", "Đáp án C", "Đáp án D"],
                "correct_answer": 0,
                "explanation": f"Giải thích cho câu {i+1}"
            })
        return questions

class ImageGenerator:
    """Handles image generation using Stable Diffusion API"""
    
    def __init__(self):
        self.api_url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
    
    def generate_illustration(self, prompt: str, topic: str) -> Optional[str]:
        """Generate educational illustration"""
        # For demonstration, return a placeholder
        # TODO: Implement actual Stable Diffusion API call
        return f"data:image/svg+xml;base64,{base64.b64encode(self.create_placeholder_svg(topic).encode()).decode()}"
    
    def create_placeholder_svg(self, topic: str) -> str:
        """Create placeholder SVG for demonstration"""
        return f'''
        <svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
            <rect width="400" height="300" fill="#f0f0f0" stroke="#ddd"/>
            <text x="200" y="150" text-anchor="middle" fill="#666" font-size="16">
                Hình minh họa cho: {topic}
            </text>
            <text x="200" y="180" text-anchor="middle" fill="#999" font-size="12">
                (Sẽ được tạo bằng AI)
            </text>
        </svg>
        '''
def login_page(db):
    st.title("🔐 Đăng nhập / Đăng ký")

    choice = st.radio("Bạn muốn:", ["Đăng nhập", "Đăng ký"])
    username = st.text_input("Tên đăng nhập:")
    password = st.text_input("Mật khẩu:", type="password")

    if choice == "Đăng ký":
        if st.button("Tạo tài khoản"):
            conn = sqlite3.connect(db.db_name)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT
                )
            """)
            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                               (username, password))
                conn.commit()
                st.success("Tạo tài khoản thành công! Hãy đăng nhập.")
            except sqlite3.IntegrityError:
                st.error("Tên đăng nhập đã tồn tại!")
            conn.close()

    elif choice == "Đăng nhập":
        if st.button("Đăng nhập"):
            conn = sqlite3.connect(db.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=? AND password=?", 
                           (username, password))
            user = cursor.fetchone()
            conn.close()
            if user:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success(f"Xin chào {username}! 🎉")
            else:
                st.error("Sai tên đăng nhập hoặc mật khẩu!")

def main():
    # Initialize components
    db = DatabaseManager()
    content_gen = ContentGenerator()
    image_gen = ImageGenerator()
    
    # ✅ Check login state
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        login_page(db)
        return
    
    # Sidebar navigation
    st.sidebar.title("🎓 EduMentor AI")
    page = st.sidebar.selectbox(
        "Chọn chức năng:",
        ["Tạo bài giảng", "Quản lý bài học", "Tạo câu hỏi", "Thống kê tiến độ", "Cài đặt"]
    )
    
    if page == "Tạo bài giảng":
        st.title("📝 Tạo Bài Giảng AI")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Thông tin bài học")
            topic = st.text_input("Chủ đề bài học:", placeholder="VD: Định lý Pythagoras")
            subject = st.selectbox("Môn học:", ["Toán", "Lý", "Hóa", "Văn", "Anh", "Sử", "Địa"])
            grade_level = st.selectbox("Cấp độ:", ["Tiểu học", "Trung học cơ sở", "Trung học phổ thông"])
            
            if st.button("🚀 Tạo Dàn Ý", type="primary"):
                if topic:
                    with st.spinner("AI đang tạo dàn ý bài giảng..."):
                        lesson_data = content_gen.generate_lesson_outline(topic, subject, grade_level)
                        st.session_state.current_lesson = lesson_data
                
        with col2:
            st.subheader("Tùy chọn nâng cao")
            include_images = st.checkbox("Tạo hình minh họa", value=True)
            include_quiz = st.checkbox("Tạo câu hỏi kiểm tra", value=True)
            lesson_duration = st.slider("Thời lượng bài học (phút)", 15, 120, 45)
        
        # Display generated content
        if 'current_lesson' in st.session_state:
            lesson = st.session_state.current_lesson
            
            st.divider()
            st.subheader("📋 Dàn Ý Bài Giảng")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**Tiêu đề:** {lesson['title']}")
                st.write(f"**Thời gian dự kiến:** {lesson['estimated_time']}")
                
                st.write("**Dàn ý chi tiết:**")
                for item in lesson['outline']:
                    st.write(f"- {item}")
                
                with st.expander("Xem nội dung chi tiết"):
                    st.write(lesson['content'])
            
            with col2:
                if include_images:
                    st.write("**Hình minh họa:**")
                    image_data = image_gen.generate_illustration(f"educational illustration for {topic}", topic)
                    st.image(image_data, width=200)
            
            # Save lesson button
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("💾 Lưu Bài Học"):
                    lesson_id = db.save_lesson(
                        lesson['title'], 
                        subject, 
                        lesson['content'], 
                        json.dumps(lesson['outline'])
                    )
                    st.success(f"Đã lưu bài học với ID: {lesson_id}")
            
            with col2:
                if include_quiz and st.button("❓ Tạo Câu Hỏi"):
                    st.session_state.show_quiz = True
    
    elif page == "Quản lý bài học":
        st.title("📚 Quản Lý Bài Học")
        
        lessons = db.get_lessons()
        
        if lessons:
            for lesson in lessons:
                with st.expander(f"{lesson['title']} - {lesson['subject']} ({lesson['created_at'][:10]})"):
                    st.write(f"**Môn học:** {lesson['subject']}")
                    st.write(f"**Ngày tạo:** {lesson['created_at']}")
                    
                    if lesson['outline']:
                        outline = json.loads(lesson['outline'])
                        st.write("**Dàn ý:**")
                        for item in outline:
                            st.write(f"- {item}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.button(f"Chỉnh sửa", key=f"edit_{lesson['id']}")
                    with col2:
                        st.button(f"Tạo Quiz", key=f"quiz_{lesson['id']}")
                    with col3:
                        st.button(f"Xóa", key=f"delete_{lesson['id']}")
        else:
            st.info("Chưa có bài học nào. Hãy tạo bài học đầu tiên!")
    
    elif page == "Tạo câu hỏi":
        st.title("❓ Tạo Câu Hỏi Kiểm Tra")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            topic_quiz = st.text_input("Chủ đề câu hỏi:", placeholder="VD: Định lý Pythagoras")
            num_questions = st.slider("Số câu hỏi:", 3, 20, 5)
            difficulty = st.selectbox("Độ khó:", ["Dễ", "Trung bình", "Khó"])
        
        with col2:
            question_type = st.radio("Loại câu hỏi:", ["Trắc nghiệm", "Tự luận", "Hỗn hợp"])
        
        if st.button("🎯 Tạo Câu Hỏi"):
            if topic_quiz:
                with st.spinner("Đang tạo câu hỏi..."):
                    questions = content_gen.generate_quiz_questions(topic_quiz, num_questions)
                    st.session_state.quiz_questions = questions
        
        # Display generated questions
        if 'quiz_questions' in st.session_state:
            st.divider()
            st.subheader("📝 Câu Hỏi Đã Tạo")
            
            for i, q in enumerate(st.session_state.quiz_questions):
                with st.expander(f"Câu {i+1}: {q['question']}"):
                    for j, option in enumerate(q['options']):
                        if j == q['correct_answer']:
                            st.write(f"✅ {chr(65+j)}. {option} (Đáp án đúng)")
                        else:
                            st.write(f"   {chr(65+j)}. {option}")
                    st.write(f"**Giải thích:** {q['explanation']}")
    
    elif page == "Thống kê tiến độ":
        st.title("📊 Thống Kê Tiến Độ Học Tập")
        
        # Sample data for demonstration
        sample_data = pd.DataFrame({
            'Ngày': pd.date_range('2024-01-01', periods=30, freq='D'),
            'Điểm số': [70, 75, 80, 85, 78, 82, 88, 90, 85, 87, 92, 89, 91, 94, 88, 
                       90, 93, 95, 92, 94, 96, 98, 95, 97, 99, 96, 98, 100, 97, 99],
            'Thời gian học (phút)': [30, 45, 35, 50, 40, 55, 60, 45, 50, 65, 70, 55, 60, 75, 50,
                                   60, 65, 70, 60, 75, 80, 85, 70, 80, 90, 75, 85, 95, 80, 90]
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_score = px.line(sample_data, x='Ngày', y='Điểm số', 
                              title='Tiến Độ Điểm Số Theo Thời Gian')
            fig_score.update_layout(height=400)
            st.plotly_chart(fig_score, use_container_width=True)
        
        with col2:
            fig_time = px.bar(sample_data.tail(10), x='Ngày', y='Thời gian học (phút)',
                             title='Thời Gian Học 10 Ngày Gần Nhất')
            fig_time.update_layout(height=400)
            st.plotly_chart(fig_time, use_container_width=True)
        
        # Summary metrics
        st.subheader("📈 Tổng Quan")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Điểm trung bình", "89.2", "↑ 2.1")
        with col2:
            st.metric("Tổng thời gian học", "1,850 phút", "↑ 150")
        with col3:
            st.metric("Bài học hoàn thành", "24", "↑ 3")
        with col4:
            st.metric("Độ chính xác trung bình", "92%", "↑ 5%")
    
    elif page == "Cài đặt":
        st.title("⚙️ Cài Đặt Hệ Thống")
        
        st.subheader("🔑 API Keys")
        deepseek_key = st.text_input("DeepSeek API Key:", type="password", 
                                    help="Nhập API key để sử dụng DeepSeek AI")
        stability_key = st.text_input("Stability AI API Key:", type="password",
                                     help="Nhập API key để tạo hình ảnh")
        
        st.subheader("🎨 Giao Diện")
        theme = st.selectbox("Chủ đề:", ["Light", "Dark", "Auto"])
        language = st.selectbox("Ngôn ngữ:", ["Tiếng Việt", "English"])
        
        st.subheader("📊 Dữ Liệu")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗃️ Xuất Dữ Liệu"):
                st.success("Dữ liệu đã được xuất!")
        with col2:
            if st.button("🔄 Đồng Bộ Cloud"):
                st.info("Tính năng sẽ được cập nhật!")
        
        st.subheader("ℹ️ Thông Tin Hệ Thống")
        st.info("""
        **EduMentor AI v1.0**
        
        Phát triển bởi: Nhóm AImpress
        - Phan Hà Thái Vinh
        - Dương Văn Thảo  
        - Dương Công Vinh
        
        Trường Đại học Công nghệ Thông tin và Truyền thông
        """)

if __name__ == "__main__":
    main() 
    