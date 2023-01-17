import pandas as pd
import streamlit as st
import requests


def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

upload = False
strategy = None 
PAGESPEED_API_KEY = None

st.title("Google Pagespeed Bulk Tester")

uploaded_file = st.file_uploader("Choose a CSV file with domains")
if uploaded_file is not None:
    data=pd.read_csv(uploaded_file, header=None)
    upload = True

strategy = st.selectbox(
    'Choose a device type',
    ('desktop', 'mobile'))
st.write('You selected:', strategy)

PAGESPEED_API_KEY= st.text_input('Enter your Google Pagespeed API key')
st.write('Your API key is ', PAGESPEED_API_KEY)
api_key = True

if upload & (strategy != None) & (PAGESPEED_API_KEY != ""):

    data.columns = ['url']
    data['pagespeed_result'] = pd.np.nan

    st.info('getting pagespeed results. this can take a while ...')
    ii = 0
    for i, r in data.iterrows():
        st.progress(ii)

        urls = [
            'http://' + r['url'],
            'https://' + r['url'],
            'http://www.' + r['url'],
            'https://www.' + r['url'],
        ]

        retry = True
        while retry:
            url = urls.pop()
            try:
                u = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?key={PAGESPEED_API_KEY}&strategy={strategy}&url={url}"
                j = requests.get(u).json()
                overall_score = j["lighthouseResult"]["categories"]["performance"]["score"] * 100
                data.loc[i, 'pagespeed_result'] = overall_score
                retry = False

            except Exception as e:
                st.error(f"Exception: {e}")
                continue

        ii += 1

    st.success('retrieved pagespeed results. you may go ahead and download them.')
    st.balloons()

    csv = convert_df(data)

    st.download_button(
    "Download Pagespeed API results",
    csv,
    f"{uploaded_file.name.replace('.csv', '')}_results_{strategy}.csv",
    "text/csv",
    key='download-csv'
    )
