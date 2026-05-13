import streamlit as st

# 1. 페이지 설정
st.set_page_config(page_title="KHEE 물류 계산기", layout="centered")
st.title("🍾 KHEE Soju 물류비 계산기")
st.info("지역과 박스 수량을 입력하면 최적 차량과 예상 운임을 산출합니다.")

# 2. 데이터베이스 (업로드해주신 요율표 기준)
rates = {
    "강남구": [68000, 100000, 140000, 180000],
    "송파구": [68000, 100000, 140000, 180000],
    "강북구": [75000, 120000, 160000, 200000],
    "화성시": [60000, 85000, 120000, 150000],
    "고창군": [220000, 280000, 380000, 500000],
}

# 3. 입력창
area = st.selectbox("📍 배송 지역 선택", list(rates.keys()))
col1, col2 = st.columns(2)
with col1:
    b375 = st.number_input("375ml 박스 수량 (4.8kg)", min_value=0, step=1, value=0)
with col2:
    b750 = st.number_input("750ml 박스 수량 (8.6kg)", min_value=0, step=1, value=0)

st.write("---")
is_via = st.checkbox("🔄 경유지 추가")
via_fee = 0
if is_via:
    via_type = st.radio("경유 유형", ["동일 행정구역 (+2만)", "타 행정구역 (+4만)"])
    via_fee = 20000 if "동일" in via_type else 40000

# 4. 계산 로직
total_weight = (b375 * 4.8) + (b750 * 8.6)
total_vol = (b375 * 0.005) + (b750 * 0.01)

truck_sizes = [0.5, 1.0, 2.5, 5.0]
selected_idx = 3
for i, size in enumerate(truck_sizes):
    if total_vol <= size and total_weight <= (size * 1100):
        selected_idx = i
        break

selected_truck = truck_sizes[selected_idx]
base_fare = rates[area][selected_idx]
manual_fee = {0.5: 20000, 1.0: 30000, 2.5: 50000, 5.0: 80000}[selected_truck]
total_cost = base_fare + via_fee + manual_fee

# 5. 결과 출력
st.divider()
st.subheader(f"🚛 추천 차량: {selected_truck}톤 트럭")
st.write(f"⚖️ **총 중량:** {total_weight:,.1f} kg | 📦 **적재 부피:** {total_vol:.2f} 톤")
st.markdown(f"### 💰 최종 예상 운임: **{total_cost:,.0f}원**")