# GPT Lab 

## Description 
GPT Lab is a user-friendly [Streamlit](https://streamlit.io) app that lets users interact with and create their own AI Assistants powered by OpenAI's GPT language model. With GPT Lab, users can chat with pre-built AI Assistants or create their own by specifying a prompt and OpenAI model parameters. Our goal is to make AI accessible and easy to use for everyone, so users can focus on designing their Assistants without worrying about the underlying infrastructure.

GPT Lab is also featured in the [Streamlit App Gallery](https://streamlit.io/gallery) among other impressive Streamlit apps.

For more insight into the development process and lessons learned while building GPT Lab, check out this [blog post](https://blog.streamlit.io/building-gpt-lab-with-streamlit/) on the official Streamlit blog.

This README will cover: 
- Accessing the app
- Running the app Locally
- Contributions
- License

## Accessing the app 
You can access the app on the Streamlit Cloud community at [gptlab.streamlit.app](https://gptlab.streamlit.app/). 

To use the app, you will need an OpenAI API key. Don't have one yet? Create one on [the OpenAI webiste](https://platform.openai.com/account/api-keys). Once you have your API key, enter it into the app when prompted. 

For optimal chatting experience, we recommend using a pay-as-you-go API key. (Free trial API keys are limited to 3 requests a minute, not enough to chat with assistants.) You will need to enter your billing information [here](https://platform.openai.com/account/billing/overview). You can learn more about OpenAI API rate limits [here](https://platform.openai.com/docs/guides/rate-limits/overview).

## Running the app locally 

To run the app locally, you will need to: 

1. Set up your own [Google Firestore](https://firebase.google.com/docs/firestore) database. 
    - GPT Lab uses four main collections: `users`, `user_hash`, `bots`, and `sessions`.
    - You will need to manually set up a `users` collection before you can run the app locally. (All otherh collections will be set up by the app). 
2. Clone this repository
3. Create a .streamlit/secrets.toml file containing the following:
```
[firestore]
db-key = "YOUR GOOGLE SERVICE ACCOUNT TOML"

[util]
global_salt = "OPTIONAL GLOBAL SALT"
```

- You will need to generate a service account JSON, and convert that JSON file to TOML. Follow the instructions [here](https://blog.streamlit.io/streamlit-firestore-continued/). 

4. In your terminal, set up your local envionrment: 
    - Set up a Python virtual environment (using `venv`, `conda`, `virtualenv`, or any other tool you prefer)
    - Install the required Python dependencies (`pip install -r app/requirements.txt`)
    - Run `streamlit run app/home.py`

## Contributions
Contributions are welcomed. Simply open up an issue and create a pull request. If you are introducing new features, please provide a detailed description of the specific use case you are addressing and setup instructions to test. 

Aside: I am new to open source, work full-time,  and have young kids, please bare with me if I don't get back to you right away. 

## License
This project is licensed under the terms of the MIT License. See [LICENSE](LICENSE) for more details.

