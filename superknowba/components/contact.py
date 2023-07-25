import streamlit as st
from streamlit_extras.buy_me_a_coffee import button


def contact() -> None:
    st.subheader("Keep in touch!")
    with st.container():
        with st.empty():
            icon, link = st.columns([0.05, 0.95])
            with icon:
                st.markdown(
                    """
                    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
                    <i class='fa-brands fa-linkedin fa-bounce'/>""",
                    unsafe_allow_html=True,
                )
            link.markdown("[Linkedin](https://www.linkedin.com/in/richieyoum/)")
        with st.empty():
            icon, link = st.columns([0.05, 0.95])
            with icon:
                st.markdown(
                    """
                    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
                    <i class="fa-brands fa-github fa-bounce"></i>""",
                    unsafe_allow_html=True,
                )
            link.markdown("[Github](https://github.com/richieyoum)")

        button(username="richieyoum", floating=False, width=225)
