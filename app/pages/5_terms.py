import streamlit as st 
import app_component as au

st.set_page_config(
    page_title="GPT Lab - Terms",
    page_icon="https://api.dicebear.com/5.x/bottts-neutral/svg?seed=gptLAb"#,
    #menu_items={"About": "GPT Lab is a user-friendly app that allows anyone to interact with and create their own AI Assistants powered by OpenAI's GPT-3 language model. Our goal is to make AI accessible and easy to use for everyone, so you can focus on designing your Assistant without worrying about the underlying infrastructure.", "Get help": None, "Report a Bug": None}
)

st.markdown(
    "<style>#MainMenu{visibility:hidden;}</style>",
    unsafe_allow_html=True
)

with st.sidebar:
    st.markdown('''
    - [Terms of Use](#terms-of-use)
    - [Privacy Policy](#privacy-policy)
    ---
    ''', unsafe_allow_html=True)

    au.st_button(url="https://twitter.com/dclin", label="Let's connect", font_awesome_icon="fa-twitter")
    au.st_button(url="https://www.buymeacoffee.com/gptlab", label="Buy me a coffee", font_awesome_icon="fa-coffee")
    au.st_button(url="https://gptlab.beehiiv.com/subscribe", label="Subscribe to news and updates", font_awesome_icon="fa-newspaper-o")


st.title("Terms")
st.write("Last updated: 2023-03-07")
st.header("Terms of Use")

st.info("""
Welcome to GPT Lab, a platform provided by GPT Lab LLC ("GPT Lab," "we," or "us"). By accessing our website, you agree to comply with the following terms of service. Please read these terms carefully. If you do not agree to these terms, you should not use our website.
""")

st.markdown("""
##### 1. Use of our Website  \n 
GPT Lab LLC provides a user-friendly platform for creating and interacting with AI Assistants powered by OpenAI's GPT-3 language model. By using our website, you agree to use it only for lawful purposes and in a manner that does not infringe the rights of or restrict or inhibit the use and enjoyment of our website by any third party. We reserve the right to terminate your access to our website at any time if we reasonably believe that you have breached any of these terms of service.

##### 2. Eligibility \n
To use GPT Lab, you must be at least 18 years of age or the legal age of majority in your jurisdiction (if different). You must also have an OpenAI API Key to access the AI models used by GPT Lab.

##### 3. OpenAI's Usage Policy  \n
OpenAI wants everyone to use their tools safely and responsibly. That’s why OpenAI has created usage policies that apply to all users of their models, tools, and services. By following these policies, users will ensure that OpenAI's technology is used for good. If OpenAI discovers that a user's product or usage doesn't follow these policies, they may ask the user to make necessary changes. Repeated or serious violations may result in further action, including suspending or terminating the user's account.

OpenAI's policies may change as they learn more about use and abuse of their models. To learn more about OpenAI's usage policy, please visit https://platform.openai.com/docs/usage-policies.

##### 4. Feedback  \n
We value your feedback on GPT Lab and appreciate any comments, suggestions, or ideas you may have for improving our platform ("Feedback"). By providing Feedback, you grant us a non-exclusive, transferable, worldwide, perpetual, irrevocable, fully-paid, royalty-free license, with the right to sublicense, to use, copy, modify, create derivative works based upon, and otherwise use the Feedback for any purpose. You acknowledge that your Feedback does not contain any confidential or proprietary information belonging to you or any third party. While we welcome your Feedback, you agree that we are not obliged to act on any Feedback you provide. You also agree to indemnify and hold GPT Lab LLC and its affiliates, officers, agents, employees, and licensors harmless from any claim or demand, including reasonable attorneys’ fees, made by any third party due to or arising out of your Feedback, as set forth in the Indemnification section below.

##### 5. Privacy Policy  \n
At GPT Lab, we take your privacy very seriously. Our application only uses your OpenAI API Key during sessions to interact with the AI models. To ensure your confidentiality and security, we use a one-way hashing algorithm on your OpenAI Key to generate your unique user identity rather than collecting or storing Personal-Identifiable-Information (PII). We also use a symmetric AES-128 encryption algorithm, with a unique key for each user, to encrypt your chat transcripts with the AI Assistants. Lastly, we do store the AI assistant prompts, which can be reviewed and audited periodically to ensure no misuse. For more information about our privacy practices, please visit our privacy policy.

##### 6. User Conduct  \n
You agree to use GPT Lab only for lawful purposes and in accordance with these Terms of Service. Specifically, you agree not to: (a) violate any applicable law or regulation; (b) maliciously try to hack or break AI Assistants by using Prompt Injection techniques; (c) share bots that do not meet our user content standard; (d) break the system in any way. You also agree to use GPT Lab in a responsible and ethical manner and to contribute to an overall positive environment for all users. This includes refraining from any behavior that promotes, incites, or engages in hate speech, discriminatory behavior, or harassment of any kind based on race, gender, sexual orientation, religion, nationality, or any other personal characteristics. This also includes creating and using AI responsibly and ethically.

##### 7. User Content  \n
You retain ownership of all GPT-3 prompts created by you on GPT Lab. You agree not to create or share AI Assistants that: (a) violate any applicable law or regulation; (b) infringe on the intellectual property, privacy, or other rights of any person, except for prompts that are inspired by existing works or ideas and do not substantially copy the intellectual property of others or violate any intellectual property laws or regulations; (c) impersonate any person or entity in a manner that is intended to deceive or mislead others, unless the impersonation is clearly designated as parody or satire, or has written permission; (d) distribute or post spam, chain letters, or pyramid schemes; (e) promote, incite, or engage in hate speech, discriminatory behavior, or harassment of any kind based on race, gender, sexual orientation, religion, nationality, or any other personal characteristics. Additionally, we recommend that you do not create AI Assistants for use in heavily regulated fields, as the legal and ethical implications of such applications can be complex and far-reaching.

As stated in our Privacy Policy, your user identifier cannot be tied to you but your chat session messages are stored. While the chat session messages are encrypted, you agree you will not provide any PII or Personal Health Information (PHI) during chat sessions. You also grant us a non-exclusive, transferable, worldwide, perpetual, irrevocable, fully-paid, royalty-free license to use, copy, modify, create derivative works based upon, and otherwise use the content for improving our platform and any other potential purposes. Finally, you agree to indemnify and hold GPT Lab LLC and its affiliates, officers, agents, employees, and licensors harmless from any claim or demand, including reasonable attorneys’ fees, made by any third party due to or arising out of any content you provide, as set forth in the Indemnification section below.

##### 8. Use of AI Assistants in Sessions  \n
GPT Lab provides a platform for creating and interacting with AI Assistants powered by OpenAI's GPT-3 language model. **While we strive to provide a safe and user-friendly experience, we cannot guarantee the accuracy or reliability of the AI Assistants created on our platform. Any advice or guidance provided by the AI Assistants should be treated as entertainment purposes only and should be taken with a grain of salt. We will not be liable for any decisions made by users based on that advice.**

As discussed in the User Content section, you agree not to provide any PII or PHI to the AI Assistants during these sessions. Please be aware that your session messages are transmitted to OpenAI's models and are recorded on our server (your user identifier cannot be tied to you and your session messages are stored encrypted). While we take appropriate measures to secure your information, we cannot guarantee the absolute security of your data. Therefore, we recommend that you do not provide any sensitive or confidential information during the chat sessions. By using the AI Assistants on our platform, you acknowledge and accept these risks. You also agree to indemnify and hold GPT Lab LLC and its affiliates, officers, agents, employees, and licensors harmless from any claim or demand, including reasonable attorneys’ fees, made by any third party due to or arising out of any chat sessions you participate in or any decisions you make based on the AI Assistants, as set forth in the Indemnification section below. 

##### 9. Termination and Suspension  \n
We reserve the right to terminate or suspend your access to GPT Lab, without notice or liability, for any reason whatsoever, including, but not limited to, a breach of these Terms of Service, and we also reserve the right to stop providing the service without advance notice. All provisions of these Terms which by their nature should survive termination shall survive, including, without limitation, ownership provisions, warranty disclaimers, indemnity, and limitations of liability.

You agree that GPT Lab LLC shall not be liable to you or any third party for any termination of your access to GPT Lab or for the discontinuation of the service. Upon termination or discontinuation, your right to use GPT Lab will immediately cease, and you must cease all use of GPT Lab and delete any stored data or information associated with it.

##### 10. Limitation of Liability  \n
GPT Lab LLC is not responsible for any direct, indirect, incidental, special, or consequential damages arising from your use of GPT Lab, including, but not limited to, any errors or omissions in any content, or any loss or damage of any kind incurred as a result of the use of any content posted, emailed, transmitted, or otherwise made available via GPT Lab.

##### 11. Indemnification  \n
You agree to indemnify and hold GPT Lab LLC and its affiliates, officers, agents, employees, and licensors harmless from any claim or demand, including reasonable attorneys’ fees, made by any third party due to or arising out of your use of GPT Lab, your violation of these Terms of Service, or your violation of any rights of another.

##### 12. Modifications  \n
GPT Lab LLC reserves the right to modify or amend these Terms of Service at any time, without notice. Your continued use of GPT Lab following any such modifications constitutes your acceptance of the modified Terms of Service.

##### 13. Governing Law  \n
These Terms of Service and any separate agreements whereby we provide you Services shall be governed by and construed in accordance with the laws of the jurisdiction in which GPT Lab LLC operates.

##### 14. Entire Agreement  \n
These Terms of Service and any policies or operating rules posted by us on the GPT Lab website or application constitute the entire agreement and understanding between you and us. These Terms of Service govern your use of the GPT Lab website or application and supersede any prior or contemporaneous agreements, communications, and proposals, whether oral or written, between you and us (including, but not limited to, any prior versions of the Terms of Service).

##### 15. Waiver and Severability  \n
Our failure to exercise or enforce any right or provision of these Terms of Service shall not constitute a waiver of such right or provision. If any provision of these Terms of Service is held to be invalid or unenforceable, such provision shall be struck and the remaining provisions shall be enforced.

##### 16. Changes to Terms of Service  \n
We reserve the right, at our sole discretion, to update, change, or replace any part of these Terms of Service by posting updates and changes to our website. It is your responsibility to check our website periodically for changes. Your continued use of or access to our website or the Service following the posting of any changes to these Terms of Service constitutes acceptance of those changes.

Contact Information
Questions about the Terms of Service should be sent to us at hello@gptlab.app.

""")

st.markdown("  \n  \n  \n  \n")

st.header("Privacy Policy")

st.markdown("""
At GPT Lab, we value your privacy and are committed to protecting it. Here's how we handle your data:

##### 1. OpenAI API Key  \n
When you sign in to GPT Lab, we require you to enter your OpenAI API Key. Our application uses your Key during sessions to interact with the AI models and to tie your AI Assistants and sessions to your unique user identity. We do not store your OpenAI API Key in plaintext. To ensure your confidentiality and security, we use a one-way hashing algorithm on your Open AI API Key to generate your unique user identity rather than collecting or storing Personal-Identifiable-Information (PII).

##### 2. AI Assistant Prompts and User Chat Session Messages  \n
Your AI Assistant Prompts and your chat session messages are transmitted and processed by OpenAI. We store both on our servers, but they are only tied to your anonymized user identifier, generated from the hashed value of your OpenAI API Key. Your information is encrypted at rest and in transit by our cloud provider (Google) and limited to authorized personnel. Additionally, we symmetrically encrypt your session messages with a unique key assigned to you before storing them on our server, ensuring they remain private on our server. The prompts are stored unencrypted and may be reviewed and audited periodically to ensure compliance with our Terms.

##### 3. Cookies  \n
We currently do not use cookies. However, we reserve the right to use cookies in the future to improve your experience and enhance the security of our platform. If we do, we will update this Privacy Policy to reflect the changes.

##### 4. "Buy Me a Coffee" and Newsletters  \n
If you choose to donate to our "Buy Me a Coffee" link (hosted by [Buy Me a Coffee](https://www.buymeacoffee.com)) (THANK YOU!) or subscribe to our newsletter (hosted by [BeeHiiv](https://www.beehiiv.com)), your email address will be collected and stored by the respective platforms for the purpose of contacting you in the future. Please refer to their respective privacy policies for more information. We do not collect and store these information from third-party services.

By using GPT Lab, you consent to this Privacy Policy. If you have any questions or concerns about our privacy policy, please contact us at hello@gptlab.app.
""")