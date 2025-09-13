# streamlit_mbti_study_recommender.py
# Streamlit app: MBTI-based Study Method Recommender
# Designed to run on Streamlit Cloud (https://streamlit.io/cloud)
# Requirements: streamlit (>=1.18), Pillow

import streamlit as st
import random
from PIL import Image
import io
import textwrap
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="MBTI Study Buddy", page_icon="📚", layout="wide")

# ---------- Helper data ----------
MBTI_LIST = [
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP",
]

STUDY_TIPS = {
    "INTJ": {
        "title": "전략적 학습자: 장기 계획 + 핵심 원리",
        "tips": [
            "학습 목표를 세부 단계로 분해해 로드맵을 만들기",
            "핵심 원리와 모델을 먼저 이해하고 예제로 확장하기",
            "조용한 환경에서 집중해서 문제를 풀기",
        ],
        "image": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?auto=format&q=75&w=1200"
    },
    "INTP": {
        "title": "분석가형: 개념 탐구 + 실험",
        "tips": [
            "개념의 '왜'를 깊게 파고들기",
            "작은 실험(코드, 문제 풀이)으로 직접 해보기",
            "혼자서 생각을 정리할 종이와 다이어그램 활용",
        ],
        "image": "https://images.unsplash.com/photo-1519744792095-2f2205e87b6f?auto=format&q=75&w=1200"
    },
    "ENTJ": {
        "title": "리더형: 목표 중심 + 효율화",
        "tips": [
            "주간/월간 학습 목표를 정하고 진행 상황 트래킹",
            "타인과의 스터디로 생산성을 높이기",
            "시간 블록을 만들어 집중 시간 확보",
        ],
        "image": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&q=75&w=1200"
    },
    "ENTP": {
        "title": "발명가형: 토론 + 다양한 접근",
        "tips": [
            "아이디어를 많이 시도하고 실패에서 배우기",
            "스터디나 디스코스에 참여해 토론하기",
            "문제를 다른 관점으로 재구성해보기",
        ],
        "image": "https://images.unsplash.com/photo-1532619675605-1b9a7d8d85c4?auto=format&q=75&w=1200"
    },
    "INFJ": {
        "title": "통찰형: 의미 중심 + 계획적인 휴식",
        "tips": [
            "학습 내용을 '나의 이야기'로 연결해 의미화하기",
            "짧은 휴식과 리플렉션 시간을 필수로 넣기",
            "시각적 노트(마인드맵)로 정리하기",
        ],
        "image": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&q=75&w=1200"
    },
    "INFP": {
        "title": "중재자형: 창의적 + 유연한 학습",
        "tips": [
            "흥미를 느끼는 주제부터 시작해 동기 부여하기",
            "작은 목표를 세워 성공 경험을 쌓기",
            "감성적 연결(음악, 그림)으로 기억 강화",
        ],
        "image": "https://images.unsplash.com/photo-1526318472351-c75fcf070ee4?auto=format&q=75&w=1200"
    },
    "ENFJ": {
        "title": "코치형: 협력 + 피드백",
        "tips": [
            "스터디 그룹에서 가르치고 피드백 받기",
            "타인의 관점에서 설명해보기(페어티칭)",
            "계획표에 다른 사람과의 약속을 넣어 책임감을 높이기",
        ],
        "image": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&q=75&w=1200"
    },
    "ENFP": {
        "title": "활동가형: 흥미 + 다양한 자극",
        "tips": [
            "프로젝트 기반 학습으로 손으로 만들어보기",
            "다양한 자료(영상, 팟캐스트, 퀴즈)로 변주 주기",
            "시간을 짧게 끊어 집중하는 포모도로 활용",
        ],
        "image": "https://images.unsplash.com/photo-1503341455253-b2e723bb3dbb?auto=format&q=75&w=1200"
    },
    "ISTJ": {
        "title": "현실주의자: 규칙적 + 꼼꼼",
        "tips": [
            "체계적 복습 스케줄(예: 1일, 7일, 30일 복습) 만들기",
            "구체적 체크리스트로 진도 관리",
            "한 번에 하나씩 마무리하는 습관 들이기",
        ],
        "image": "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&q=75&w=1200"
    },
    "ISFJ": {
        "title": "수호자형: 꾸준함 + 세심함",
        "tips": [
            "안정된 환경에서 규칙적으로 공부하기",
            "노트 정리와 예습·복습의 철저한 실행",
            "작은 보상으로 동기 유지하기",
        ],
        "image": "https://images.unsplash.com/photo-1529333166437-7750a6dd5a70?auto=format&q=75&w=1200"
    },
    "ESTJ": {
        "title": "관리자형: 목표 달성 + 관리",
        "tips": [
            "우선순위를 정해 중요한 것부터 해결",
            "성과 측정(퀴즈, 자가점검)으로 효율 확인",
            "팀 프로젝트에서 리더 역할 맡아 실행력 발휘",
        ],
        "image": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&q=75&w=1200"
    },
    "ESFJ": {
        "title": "사교가형: 협력 + 규율",
        "tips": [
            "친구와 스터디 약속 잡아 꾸준히 참석",
            "교사·동료와의 피드백을 적극 활용",
            "시각적 플래너로 하루를 조직하기",
        ],
        "image": "https://images.unsplash.com/photo-1554774853-b4a4f62d1f22?auto=format&q=75&w=1200"
    },
    "ISTP": {
        "title": "장인형: 실습 + 즉흥성",
        "tips": [
            "실습 중심으로 '해보며 배우기'를 선호",
            "도전적인 문제를 단계별로 분해해 해결",
            "빠른 피드백(자체 테스트)으로 개선",
        ],
        "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&q=75&w=1200"
    },
    "ISFP": {
        "title": "모험가형: 감각적 + 느긋",
        "tips": [
            "시각적 자료와 감성적 동기(좋아하는 배경음악) 활용",
            "완벽보다 성취 경험을 우선시하기",
            "짧은 세션으로 규칙적 학습 유지",
        ],
        "image": "https://images.unsplash.com/photo-1504198453319-5ce911bafcde?auto=format&q=75&w=1200"
    },
    "ESTP": {
        "title": "촉진자형: 액션 + 경쟁",
        "tips": [
            "실제 문제 중심 학습으로 흥미 유지",
            "짧은 시간 안에 해내는 챌린지 형식 도입",
            "스피드 퀴즈로 복습 습관화",
        ],
        "image": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&q=75&w=1200"
    },
    "ESFP": {
        "title": "연예인형: 활기 + 체험",
        "tips": [
            "프로젝트·발표 중심으로 활동형 학습 선호",
            "시각 자료나 이야기로 내용을 꾸미기",
            "친구와 함께하는 실습으로 동기 유지",
        ],
        "image": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&q=75&w=1200"
    },
}

# ---------- UI ----------

# Background style + floating images
BACKGROUND_CSS = """
<style>
body { background: linear-gradient(120deg, #f0f8ff 0%, #fffaf0 100%); }
.float-img { animation: floaty 6s ease-in-out infinite; border-radius: 12px; box-shadow: 0 8px 30px rgba(0,0,0,0.12); }
@keyframes floaty {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-12px); }
  100% { transform: translateY(0px); }
}
.card { background: rgba(255,255,255,0.7); padding: 18px; border-radius: 16px; }
.tip { margin-bottom: 8px; }
.small { font-size: 0.9rem; color: #333333; }
</style>
"""

st.markdown(BACKGROUND_CSS, unsafe_allow_html=True)

# Header
col1, col2 = st.columns([3,1])
with col1:
    st.title("📚 MBTI Study Buddy — 내 유형에 딱 맞는 공부법")
    st.write("MBTI를 선택하면 **당신에게 가장 잘 맞는 공부법**과 실용 팁, 영감 이미지들을 한 번에 보여줍니다. 재미있는 효과도 준비했어요!")
with col2:
    st.image("https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&q=75&w=800", width=160)

# Sidebar
st.sidebar.header("설정")
mbti_choice = st.sidebar.selectbox("당신의 MBTI 유형을 선택하세요", options=["선택하세요"]+MBTI_LIST)
show_random = st.sidebar.checkbox("랜덤 이미지와 팁을 섞기", value=True)
confetti_toggle = st.sidebar.checkbox("축하 효과 사용하기(버튼 클릭 시)", value=True)

# Main content
if mbti_choice and mbti_choice != "선택하세요":
    profile = STUDY_TIPS.get(mbti_choice, None)
    if not profile:
        st.error("아직 이 유형에 대한 데이터가 준비되지 않았습니다.")
    else:
        # Top card
        top_col1, top_col2 = st.columns([2,3])
        with top_col1:
            st.markdown(f"<div class='card'><h2>{mbti_choice} — {profile['title']}</h2>", unsafe_allow_html=True)
            st.markdown("<p class='small'>당신의 성향에 최적화된 실전 공부 팁</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # show image + tips
        mid_col1, mid_col2 = st.columns([1,1])
        with mid_col1:
            img_url = profile['image']
            # Optionally shuffle image choices by picking related Unsplash pics
            st.image(img_url, caption=f"{mbti_choice} vibe", use_column_width=True, clamp=True)

        with mid_col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            for i, tip in enumerate(profile['tips'], start=1):
                st.markdown(f"<div class='tip'><b>{i}.</b> {tip}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Extra playful visuals: 3 related thumbnails
        thumbs = [profile['image']]
        # create a few related images by swapping query keywords (simple heuristic)
        related_keywords = ["study","books","focus","study desk","notebook"]
        # pick random related images from unsplash source URLs (no API key required for simple images)
        for k in random.sample(related_keywords, 3):
            thumbs.append(f"https://source.unsplash.com/collection/9581285/800x600?{k}")

        st.markdown("### 영감 이미지 갤러리")
        cols = st.columns(3)
        for c, url in zip(cols, thumbs):
            with c:
                st.image(url, use_column_width=True, caption="inspo", clamp=True, output_format='auto')

        # Fun: Quick personalized study plan generator
        st.markdown("---")
        st.subheader("오늘의 30분 집중 플랜 만들기 ✨")
        focus_topic = st.text_input("오늘 집중할 주제/과목을 적어보세요", value="수학 - 이차방정식")
        difficulty = st.selectbox("난이도", options=["쉬움","보통","어려움"], index=1)

        if st.button("플랜 생성하기 🚀"):
            # make a tiny plan depending on MBTI style
            base = []
            if mbti_choice in ["INTJ","ENTJ","ISTJ","ESTJ"]:
                base = ["목표 설정 5분","핵심 개념 학습 15분","문제 풀이 8분","복습·요약 2분"]
            elif mbti_choice in ["INFP","ENFP","ISFP","ESFP"]:
                base = ["흥미 유발 5분 (짧은 영상)","핵심 활동 15분","창의적 정리 6분","짧은 복습 4분"]
            else:
                base = ["개념 정리 6분","실습/문제풀이 18분","오답 정리 4분","자기평가 2분"]

            # adapt by difficulty
            if difficulty == "어려움":
                base[1] = base[1].replace("15","20") if "15" in base[1] else base[1]
            plan_md = "\n".join([f"- {s}" for s in base])
            st.success(f"{mbti_choice} 맞춤 30분 플랜 — {focus_topic}")
            st.markdown(plan_md)

            # Show confetti if enabled
            if confetti_toggle:
                # render a tiny HTML snippet that fires confetti once
                confetti_html = """
                <canvas id='canvas'></canvas>
                <script src='https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js'></script>
                <script>
                  var myCanvas = document.getElementById('canvas');
                  myCanvas.width = window.innerWidth;
                  myCanvas.height = 300;
                  confetti.create(myCanvas, { resize: true, useWorker: true })({ particleCount: 120, spread: 160 });
                </script>
                <style>canvas{position:relative; width:100%; height:150px;}</style>
                """
                components.html(confetti_html, height=160)

        # Extra: quick printable study checklist
        st.markdown("---")
        st.subheader("간단 체크리스트 (프린트 가능)")
        checklist = st.checkbox("체크리스트 보이기/숨기기")
        if checklist:
            st.markdown(textwrap.dedent(f"""
            - [ ] 오늘의 학습 목표 설정
            - [ ] 핵심 개념 15분 이해
            - [ ] 문제 풀이 15분
            - [ ] 오답 노트 정리
            - [ ] 복습/요약 5분
            """))

        # Footer flourish
        st.markdown("<div style='text-align:center; margin-top:18px;'>🎧 좋아하는 배경음악으로 몰입도를 높여보세요 — 25분 집중 후 5분 휴식!</div>", unsafe_allow_html=True)

else:
    st.info("왼쪽 사이드바에서 MBTI 유형을 선택해 주세요. 예시로 골라볼까요? 😄")
    # playful illustrations when nothing selected
    placeholder_cols = st.columns(3)
    for c in placeholder_cols:
        c.image("https://images.unsplash.com/photo-1515879218367-8466d910aaa4?auto=format&q=75&w=800", use_column_width=True)

# ---------- End ----------

# Notes for deployment (show in app footer)
st.markdown("\n---\n*이 앱은 데모용입니다. Streamlit Cloud에 배포하려면 requirements.txt에 `streamlit`과 `Pillow`를 추가하세요.*")
