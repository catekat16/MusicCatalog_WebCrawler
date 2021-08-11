import streamlit as st
import streamlit.components.v1 as components
import os
from musiccatalog_webcrawler import *

#uploaded_file = st.file_uploader('Upload the input file with song titles (.xlsx format)')
#file_text = ''

#if uploaded_file is not None:
#    uploaded_file.seek(0)

def get_table_download_link(dataframe3):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = dataframe3.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Download csv file</a>'
    return href
    
def file_selector(folder_path='.'):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('Select a file', filenames)
    return os.path.join(folder_path, selected_filename)

filename = file_selector()
st.write('You selected `%s`' % filename)
[(seconds_elapsed, average_seconds),[num_recorded, total_num_items, accuracy, match]] = run_main(filename) # [(seconds_elapsed, average_seconds),output_info]

st.write('Check out the output file!')
#st.write('Accounting for `%s` songs out of `%x`' % (num_recorded, total_num_items))
st.write('Percentage match against manually inputted file: `%s`' % accuracy)
#st.write('`%s` matches out of `%x`' % (match, num_recorded))


st.write('Total time elapsed (in seconds):`%s`' % seconds_elapsed)
st.write('Average time taken for each song (in seconds): `%s`' % average_seconds)

#st.markdown(get_table_download_link(dataframe3), unsafe_allow_html=True)

