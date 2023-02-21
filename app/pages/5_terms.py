import streamlit as st 

st.set_page_config(
    page_title="GPT Lab - Terms",
    page_icon="https://api.dicebear.com/5.x/bottts-neutral/svg?seed=gptLAb"#,
    #menu_items={"About": "GPT Lab is a user-friendly app that allows anyone to interact with and create their own AI Assistants powered by OpenAI's GPT-3 language model. Our goal is to make AI accessible and easy to use for everyone, so you can focus on designing your Assistant without worrying about the underlying infrastructure.", "Get help": None, "Report a Bug": None}
)

st.markdown(
    "<style>#MainMenu{visibility:hidden;}</style>",
    unsafe_allow_html=True
)


st.sidebar.markdown('''
- [Terms of Use](#terms-of-use)
- [Privacy Policy](#privacy-policy)
''', unsafe_allow_html=True)

st.title("Terms")
st.write("Last updated: 2023-02-21")
st.header("Terms of Use")

st.info("""
Welcome to GPT Lab! By accessing our website, you agree to comply with the following terms of service. Please read these terms carefully. If you do not agree to these terms, you should not use our website.
""")

st.markdown("""
##### 1. Use of our Website  \n 
GPT Lab provides a user-friendly platform for creating and interacting with AI Assistants powered by OpenAI's GPT-3 language model. By using our website, you agree to use it only for lawful purposes and in a manner that does not infringe the rights of or restrict or inhibit the use and enjoyment of our website by any third party. We reserve the right to terminate your access to our website at any time if we reasonably believe that you have breached any of these terms of service.

##### 2. Eligibility \n
To use GPT Lab, you must be at least 18 years of age or the legal age of majority in your jurisdiction (if different). You must also have an OpenAI API Key to access the AI models used by GPT Lab.

##### 3. OpenAI's Usage Policy  \n
OpenAI wants everyone to use their tools safely and responsibly. That’s why OpenAI has created usage policies that apply to all users of their models, tools, and services. By following these policies, users will ensure that OpenAI's technology is used for good. If OpenAI discovers that a user's product or usage doesn't follow these policies, they may ask the user to make necessary changes. Repeated or serious violations may result in further action, including suspending or terminating the user's account.

OpenAI's policies may change as they learn more about use and abuse of their models. To learn more about OpenAI's usage policy, please visit https://platform.openai.com/docs/usage-policies.

##### 4. Privacy Policy  \n
At GPT Lab, we take your privacy very seriously. Our application only uses your OpenAI API Key during sessions to interact with the AI models. To ensure your confidentiality and security, we use a one-way hashing algorithm on your OpenAI Key to generate your unique user identity rather than collecting or storing Personal-Identifiable-Information (PII). We do store the chat session messages, which can be reviewed and audited periodically to ensure no misuse. For more information about our privacy practices, please visit our privacy policy.

##### 5. User Conduct  \n
You agree to use GPT Lab only for lawful purposes and in accordance with these Terms of Service. Specifically, you agree not to: (a) violate any applicable law or regulation; (b) maliciously try to hack or break AI Assistants by using Prompt Injection techniques; (c) share bots that do not meet our user content standard; (d) break the system in any way.

##### 6. User Content  \n
You retain ownership of all GPT-3 prompts created by you on GPT Lab. You agree not to create or share AI Assistants that: (a) violate any applicable law or regulation; (b) infringe on the intellectual property, privacy, or other rights of any person, except for prompts that are inspired by existing works or ideas and do not substantially copy the intellectual property of others or violate any intellectual property laws or regulations; (c) impersonate any person or entity in a manner that is intended to deceive or mislead others, unless the impersonation is clearly designated as parody or satire, or has written permission; (d) distribute or post spam, chain letters, or pyramid schemes; (e) promote, incite, or engage in hate speech, discriminatory behavior, or harassment of any kind based on race, gender, sexual orientation, religion, nationality, or any other personal characteristics.

Additionally, we recommend that you do not create AI Assistants for use in heavily regulated fields, as the legal and ethical implications of such applications can be complex and far-reaching.

##### 7. Termination and Suspension  \n
We reserve the right to terminate or suspend your access to GPT Lab, without notice or liability, for any reason whatsoever, including, but not limited to, a breach of these Terms of Service, and we also reserve the right to stop providing the service without advance notice. All provisions of these Terms which by their nature should survive termination shall survive, including, without limitation, ownership provisions, warranty disclaimers, indemnity, and limitations of liability.

You agree that GPT Lab shall not be liable to you or any third party for any termination of your access to GPT Lab or for the discontinuation of the service. Upon termination or discontinuation, your right to use GPT Lab will immediately cease, and you must cease all use of GPT Lab and delete any stored data or information associated with it.

##### 8. Limitation of Liability  \n
GPT Lab is not responsible for any direct, indirect, incidental, special, or consequential damages arising from your use of GPT Lab, including, but not limited to, any errors or omissions in any content, or any loss or damage of any kind incurred as a result of the use of any content posted, emailed, transmitted, or otherwise made available via GPT Lab.

##### 9. Indemnification  \n
You agree to indemnify and hold GPT Lab and its affiliates, officers, agents, employees, and licensors harmless from any claim or demand, including reasonable attorneys’ fees, made by any third party due to or arising out of your use of GPT Lab, your violation of these Terms of Service, or your violation of any rights of another.

##### 10. Modifications  \n
GPT Lab reserves the right to modify or amend these Terms of Service at any time, without notice. Your continued use of GPT Lab following any such modifications constitutes your acceptance of the modified Terms of Service.

##### 11. Governing Law  \n
These Terms of Service and any separate agreements whereby we provide you Services shall be governed by and construed in accordance with the laws of the jurisdiction in which GPT Lab operates.

##### 12. Entire Agreement  \n
These Terms of Service and any policies or operating rules posted by us on the GPT Lab website or application constitute the entire agreement and understanding between you and us. These Terms of Service govern your use of the GPT Lab website or application and supersede any prior or contemporaneous agreements, communications, and proposals, whether oral or written, between you and us (including, but not limited to, any prior versions of the Terms of Service).

##### 13. Waiver and Severability  \n
Our failure to exercise or enforce any right or provision of these Terms of Service shall not constitute a waiver of such right or provision. If any provision of these Terms of Service is held to be invalid or unenforceable, such provision shall be struck and the remaining provisions shall be enforced.

##### 14. Changes to Terms of Service  \n
We reserve the right, at our sole discretion, to update, change, or replace any part of these Terms of Service by posting updates and changes to our website. It is your responsibility to check our website periodically for changes. Your continued use of or access to our website or the Service following the posting of any changes to these Terms of Service constitutes acceptance of those changes.

Contact Information
Questions about the Terms of Service should be sent to us at hello@gptlab.app.

""")

st.markdown("  \n  \n  \n  \n")

st.header("Privacy Policy")

st.markdown("""
At GPT Lab, we value your privacy and are committed to protecting it. Here's how we handle your data:

##### 1. OpenAI API Key  \n
When you sign in to GPT Lab, we require you to enter your OpenAI API Key. Our application uses your Key during sessions to interact with the AI models and to tie your AI Assistants and sessions to your unique user identity. We do not store your OpenAI API Key. To ensure your confidentiality and security, we use a one-way hashing algorithm on your Open AI Key to generate your unique user identity rather than collecting or storing Personal-Identifiable-Information (PII).

##### 2. Chat Session Messages  \n
We store chat session messages on our servers. While we do not collect any Personal-Identifiable-Information (PII) in the process of generating the chat session messages, some PII may be contained within the messages. These messages can be reviewed/audited periodically to ensure no misuse.

##### 3. Cookies  \n
We currently do not use cookies.

##### 4. "Buy Me a Coffee" and Newsletters  \n
If you choose to donate to our "Buy Me a Coffee" link (hosted by [Buy Me a Coffee](https://www.buymeacoffee.com)) (THANK YOU!) or subscribe to our newsletter (hosted by [BeeHiiv](https://www.beehiiv.com)), your email address will be collected and stored by the respective platforms for the purpose of contacting you in the future. Please refer to their respective privacy policies for more information.

By using GPT Lab, you consent to this Privacy Policy. If you have any questions or concerns about our privacy policy, please contact us at hello@gptlab.app.
""")