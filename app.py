import streamlit as st

st.set_page_config(page_title="KHEE 물류 계산기", layout="wide")
st.title("🍾 KHEE Soju 물류비 계산기")

# ─── 요율표 (지역별 0.5 / 1 / 2.5 / 5톤 순) ─────────────────────────────
RATES = {
    "강남구":  [68000, 100000, 140000, 180000],
    "송파구":  [68000, 100000, 140000, 180000],
    "강북구":  [75000, 120000, 160000, 200000],
    "화성시":  [60000,  85000, 120000, 150000],
    "고창군": [220000, 280000, 380000, 500000],
}

# 동일/타 행정구역 판단을 위한 상위 행정구역
REGION_PARENT = {
    "강남구": "서울특별시",
    "송파구": "서울특별시",
    "강북구": "서울특별시",
    "화성시": "경기도",
    "고창군": "전라북도",
}

TRUCK_SIZES   = [0.5,   1.0,   2.5,    5.0]
MAX_BOXES_375 = [100,   200,   500,   1000]   # 차량별 375ml 최대 박스
MAX_BOXES_750 = [52.5,  105,   262.5,  525]   # 차량별 750ml 최대 박스
MANUAL_FEE    = [20000, 30000, 50000, 80000]  # 차량별 수작업비

PRODUCTS_375 = ["22 375", "22 375K", "38 375", "38 375K"]
PRODUCTS_750 = ["22 750", "22 750K", "38 750", "38 750K"]


def box_inputs(products: list[str], key_prefix: str) -> int:
    """품목별 박스 수량 입력 UI, 합계 반환"""
    cols = st.columns(len(products))
    total = 0
    for col, product in zip(cols, products):
        with col:
            total += st.number_input(
                product, min_value=0, step=1, value=0, key=f"{key_prefix}_{product}"
            )
    return total


def find_truck(b375: int, b750: int):
    """최소 적합 차량 인덱스와 적재율 반환. 5톤도 초과 시 (None, 초과율) 반환."""
    for i in range(len(TRUCK_SIZES)):
        ratio = (b375 / MAX_BOXES_375[i]) + (b750 / MAX_BOXES_750[i])
        if ratio <= 1.0:
            return i, ratio
    # 5톤 초과
    i = len(TRUCK_SIZES) - 1
    ratio = (b375 / MAX_BOXES_375[i]) + (b750 / MAX_BOXES_750[i])
    return None, ratio


# ════════════════════════════════════════════════════════════
# 1. 메인 배송 입력
# ════════════════════════════════════════════════════════════
st.subheader("📦 메인 배송")
main_area = st.selectbox("배송 지역", list(RATES.keys()), key="main_area")

col_l, col_r = st.columns(2)
with col_l:
    st.markdown("**375ml 품목 (박스 수량)**")
    main_375 = box_inputs(PRODUCTS_375, "m375")
with col_r:
    st.markdown("**750ml 품목 (박스 수량)**")
    main_750 = box_inputs(PRODUCTS_750, "m750")

# ════════════════════════════════════════════════════════════
# 2. 경유지 입력
# ════════════════════════════════════════════════════════════
st.divider()
is_via = st.checkbox("🔄 경유지 추가")

via_fee   = 0
via_375   = 0
via_750   = 0
via_label = ""

if is_via:
    st.subheader("🗺️ 경유지")
    via_area = st.selectbox("경유지 지역", list(RATES.keys()), key="via_area")

    # 자동 동일/타 행정구역 판단
    if REGION_PARENT[main_area] == REGION_PARENT[via_area]:
        via_label = "동일 행정구역"
        via_fee   = 20000
        st.success(f"✅ {via_label} 경유  →  +{via_fee:,}원")
    else:
        via_label = "타 행정구역"
        via_fee   = 40000
        st.warning(f"⚠️ {via_label} 경유  →  +{via_fee:,}원")

    col_vl, col_vr = st.columns(2)
    with col_vl:
        st.markdown("**경유지 375ml 품목 (박스 수량)**")
        via_375 = box_inputs(PRODUCTS_375, "v375")
    with col_vr:
        st.markdown("**경유지 750ml 품목 (박스 수량)**")
        via_750 = box_inputs(PRODUCTS_750, "v750")

# ════════════════════════════════════════════════════════════
# 3. 계산
# ════════════════════════════════════════════════════════════
total_375 = main_375 + via_375
total_750 = main_750 + via_750
total_weight = total_375 * 4.8 + total_750 * 8.6

truck_idx, ratio = find_truck(total_375, total_750)
exceeded = truck_idx is None
if exceeded:
    truck_idx = len(TRUCK_SIZES) - 1  # 5톤 기준으로 금액 산출

truck_size   = TRUCK_SIZES[truck_idx]
base_fare    = RATES[main_area][truck_idx]
manual_fee   = MANUAL_FEE[truck_idx]
total_cost   = base_fare + manual_fee + via_fee

# ════════════════════════════════════════════════════════════
# 4. 결과 출력
# ════════════════════════════════════════════════════════════
st.divider()
st.subheader("📊 계산 결과")

# 수량 요약
c1, c2, c3 = st.columns(3)
c1.metric("375ml 합계",   f"{total_375} 박스")
c2.metric("750ml 합계",   f"{total_750} 박스")
c3.metric("총 중량",      f"{total_weight:,.1f} kg")

# 적재율 / 초과 여부
st.write("")
if exceeded:
    st.error(
        f"🚨 **적재량 초과** — 5톤 기준 적재율 {ratio*100:.1f}%  "
        f"(100% 초과)  |  분차 배송 검토 필요"
    )
else:
    pct = ratio * 100
    color = "🟡" if pct > 80 else "🟢"
    st.info(f"{color} 추천 차량: **{truck_size}톤**  |  적재율: **{pct:.1f}%**")

# 운임 내역
st.write("---")
st.write(f"- 기본 운임  ({main_area} / {truck_size}톤): **{base_fare:,}원**")
st.write(f"- 수작업비: **{manual_fee:,}원**")
if is_via:
    st.write(f"- 경유비 ({via_label}): **{via_fee:,}원**")

st.write("")
if exceeded:
    st.error(f"### 💰 최종 운임 (5톤 초과 기준): **{total_cost:,}원**")
else:
    st.markdown(f"### 💰 최종 예상 운임: **{total_cost:,}원**")
