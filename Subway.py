import pandas as pd
import streamlit as st

# -----------------------------------
# CSV 파일 불러오기
# -----------------------------------
def load_data(uploaded_file):

    encodings = ['cp949', 'euc-kr', 'utf-8']
    df = None

    for enc in encodings:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding=enc)
            st.success(f'인코딩 성공: {enc}')
            break
        except:
            continue

    if df is None:
        st.error('CSV 파일을 읽을 수 없습니다.')
        st.stop()

    # 컬럼 공백 제거
    df.columns = df.columns.str.strip()

    return df


# -----------------------------------
# 총 혼잡도 계산
# -----------------------------------
def calculate_total_congestion(df):

    # 시간 컬럼 추출
    time_cols = df.columns[5:]

    # 숫자형 변환
    for col in time_cols:
        df[col] = pd.to_numeric(
            df[col],
            errors='coerce'
        ).fillna(0)

    # 총 혼잡도 계산
    df['총혼잡도'] = df[time_cols].sum(axis=1)

    return df, time_cols


# -----------------------------------
# 전체 호선 평균 혼잡도 분석
# -----------------------------------
def analyze_lines(df):

    line_result = (
        df.groupby('호선')['총혼잡도']
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    return line_result


# -----------------------------------
# 가장 혼잡한 노선 추출
# -----------------------------------
def get_most_congested_line(line_result):

    return line_result.iloc[0]['호선']


# -----------------------------------
# 특정 노선 데이터 추출
# -----------------------------------
def filter_line(df, line_name):

    return df[df['호선'] == line_name].copy()


# -----------------------------------
# 역별 평균 혼잡도 분석
# -----------------------------------
def analyze_stations(df_line):

    station_result = (
        df_line.groupby('출발역')['총혼잡도']
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    return station_result


# -----------------------------------
# 혼잡 역 TOP10
# -----------------------------------
def top10_stations(station_result):

    return station_result.head(10)


# -----------------------------------
# 시간대별 평균 혼잡도 분석
# -----------------------------------
def analyze_time(df_line, time_cols):

    time_result = {}

    for col in time_cols:
        time_result[col] = df_line[col].mean()

    time_df = pd.DataFrame({
        '시간대': list(time_result.keys()),
        '평균혼잡도': list(time_result.values())
    })

    return time_df


# -----------------------------------
# 출퇴근 시간 비교
# -----------------------------------
def compare_rush_hours(df_line):

    # 자동으로 시간 컬럼 찾기
    morning_cols = [
        col for col in df_line.columns
        if '7시' in str(col) or '8시' in str(col)
    ]

    evening_cols = [
        col for col in df_line.columns
        if '18시' in str(col) or '19시' in str(col)
    ]

    morning_avg = 0
    evening_avg = 0

    if morning_cols:
        morning_avg = df_line[morning_cols].mean().mean()

    if evening_cols:
        evening_avg = df_line[evening_cols].mean().mean()

    return morning_avg, evening_avg


# -----------------------------------
# 메인 함수
# -----------------------------------
def main():

    st.set_page_config(
        page_title='서울 지하철 혼잡도 분석',
        layout='wide'
    )

    st.title('서울 지하철 혼잡도 분석 프로그램')

    # 파일 업로드
    uploaded_file = st.file_uploader(
        'CSV 파일 업로드',
        type=['csv']
    )

    if uploaded_file is not None:

        # 데이터 불러오기
        df = load_data(uploaded_file)

        # 원본 데이터 출력
        st.subheader('원본 데이터 미리보기')
        st.dataframe(df.head())

        # 총 혼잡도 계산
        df, time_cols = calculate_total_congestion(df)

        # -----------------------------------
        # 1단계: 전체 노선 분석
        # -----------------------------------
        st.subheader('전체 호선 평균 혼잡도')

        line_result = analyze_lines(df)

        st.dataframe(line_result)

        # 막대 차트
        st.bar_chart(
            line_result.set_index('호선')
        )

        # 가장 혼잡한 노선 추출
        most_line = get_most_congested_line(line_result)

        st.success(f'가장 혼잡한 노선: {most_line}')

        # -----------------------------------
        # 2단계: 가장 혼잡한 노선 분석
        # -----------------------------------
        st.subheader(f'{most_line} 역별 평균 혼잡도')

        df_line = filter_line(df, most_line)

        station_result = analyze_stations(df_line)

        st.dataframe(station_result)

        # TOP10
        st.subheader(f'{most_line} 혼잡 역 TOP10')

        top10 = top10_stations(station_result)

        st.dataframe(top10)

        # -----------------------------------
        # 3단계: 시간대별 분석
        # -----------------------------------
        st.subheader(f'{most_line} 시간대별 평균 혼잡도')

        time_result = analyze_time(df_line, time_cols)

        st.dataframe(time_result)

        # 선 그래프
        st.line_chart(
            time_result.set_index('시간대')
        )

        # -----------------------------------
        # 출퇴근 시간 비교
        # -----------------------------------
        st.subheader('출근 시간대 vs 퇴근 시간대')

        morning_avg, evening_avg = compare_rush_hours(df_line)

        st.write(f'출근 시간대 평균 혼잡도: {morning_avg:.2f}')
        st.write(f'퇴근 시간대 평균 혼잡도: {evening_avg:.2f}')


# -----------------------------------
# 프로그램 실행
# -----------------------------------
if __name__ == '__main__':
    main()