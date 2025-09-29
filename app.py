import streamlit as st
import pandas as pd
from parser import parse_content
from converter import save_to_csv_and_db
from db import init_db, fetch_table
from chatbot import get_chatbot_response
from manager import find_similar_concepts, check_similarity_before_save

DB_PATH = "suri.db"
init_db(DB_PATH)

st.title("📂 수리 사주 분석 & DB 저장 시스템")

tab1, tab2, tab3, tab4 = st.tabs(["문서 업로드", "DB 조회", "사주 챗봇", "데이터 관리"])

with tab1:
    st.subheader("📄 텍스트 파일 업로드")
    uploaded_files = st.file_uploader(
        "개념, 규칙, 사례가 포함된 파일을 여러 개 선택할 수 있습니다.",
        type=["txt", "md"],
        accept_multiple_files=True
    )

    if uploaded_files:
        all_parsed_data = {"concepts": [], "rules": [], "cases": []}
        for uploaded_file in uploaded_files:
            try:
                text = uploaded_file.read().decode("utf-8")
                parsed_per_file = parse_content(text, source=uploaded_file.name)
                all_parsed_data["concepts"].extend(parsed_per_file["concepts"])
                all_parsed_data["rules"].extend(parsed_per_file["rules"])
                all_parsed_data["cases"].extend(parsed_per_file["cases"])
            except Exception as e:
                st.error(f"'{uploaded_file.name}' 파일 처리 중 오류 발생: {e}")

        st.subheader("📌 전체 파싱 결과 미리보기")
        st.json(all_parsed_data)

        if st.button("DB 및 CSV로 저장"):
            with st.spinner("기존 데이터와 유사도를 검사합니다..."):
                new_concepts = all_parsed_data.get("concepts", [])
                similar_items = check_similarity_before_save(new_concepts, DB_PATH, threshold=0.8)

            if similar_items:
                st.error("⚠️ **저장 중단: 유사/중복 항목 발견**")
                st.info("새로 추가하려는 개념 중 일부가 DB에 이미 있는 내용과 매우 유사합니다. 데이터 품질을 위해 자동 저장을 중단했습니다.")
                st.markdown("**유사 항목 목록:**")
                similar_df = pd.DataFrame(similar_items)
                similar_df.rename(columns={
                    'new_item_name': '새로운 개념',
                    'existing_item_name': 'DB의 유사 개념',
                    'similarity': '유사도'
                }, inplace=True)
                st.table(similar_df)
                st.warning("'데이터 관리' 탭에서 기존 데이터를 확인 및 정리하시거나, 원본 파일을 수정한 후 다시 업로드해주세요.")
            else:
                st.success("✅ 유사/중복된 개념이 없습니다. 데이터를 안전하게 저장합니다.")
                save_to_csv_and_db(all_parsed_data, DB_PATH)
                st.success(f"총 {len(uploaded_files)}개 파일의 데이터를 DB 및 CSV 파일로 저장을 완료했습니다!")
                st.balloons()

with tab2:
    st.subheader("📊 저장된 데이터 조회")
    table_to_view = st.selectbox("조회할 테이블 선택", ["rules", "concepts", "cases"])
    if table_to_view:
        df = fetch_table(DB_PATH, table_to_view)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label="📥 CSV 파일로 다운로드",
                data=csv,
                file_name=f"{table_to_view}_backup_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )
        else:
            st.warning("선택한 테이블에 데이터가 없습니다.")

with tab3:
    st.subheader("💬 사주 챗봇")
    st.info("사주 명식(예: 庚子 辛巳 癸卯 甲寅)을 입력하여 분석하거나, 궁금한 용어(예: 겁살)를 질문하세요.")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if prompt := st.chat_input("사주 명식 또는 질문을 입력하세요..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("답변을 생성하는 중입니다..."):
                response = get_chatbot_response(prompt)
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

with tab4:
    st.subheader("🧬 유사/중복 데이터 관리")
    st.info("DB에 저장된 '개념(concepts)' 데이터 중 내용이 유사한 항목들을 찾아 그룹으로 보여줍니다.")
    similarity_threshold = st.slider("유사도 임계값 설정", 0.1, 1.0, 0.7, 0.05)
    if st.button("유사 개념 찾기"):
        with st.spinner("유사도 분석을 실행 중입니다... (데이터가 많으면 시간이 걸릴 수 있습니다)"):
            similar_groups = find_similar_concepts(DB_PATH, threshold=similarity_threshold)
            if not similar_groups:
                st.success("지정한 임계값 이상의 유사한 개념을 찾지 못했습니다.")
            else:
                st.success(f"총 {len(similar_groups)}개의 유사 개념 그룹을 찾았습니다.")
                for i, group in enumerate(similar_groups):
                    avg_sim = group['avg_similarity']
                    items = group['items']
                    with st.expander(f"그룹 {i+1}: '{items[0]['name']}' 등 {len(items)}개 항목 (평균 유사도: {avg_sim:.2f})"):
                        for item in items:
                            st.markdown(f"---")
                            st.markdown(f"**ID:** `{item['concept_id']}` | **출처:** `{item['source']}`")
                            st.markdown(f"**이름:** {item['name']}")
                            # ⭐️ 여기를 수정했습니다! ⭐️
                            # key에 그룹 번호(i)를 추가하여 고유성을 보장합니다.
                            st.text_area("정의:", item['definition'], height=100, key=f"group_{i}_def_{item['id']}")
        
        st.markdown("---")
        st.warning("⚠️ **주의:** 현재 버전은 유사 항목을 찾아 보여주기만 합니다. 실제 병합/삭제 기능은 다음 단계에서 구현할 수 있으며, 현재는 이 목록을 참고하여 DB를 직접 수정해야 합니다.")

