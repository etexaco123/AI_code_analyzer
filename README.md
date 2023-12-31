
# AI Code Analyzer Using Large Language Models

This project allows you to upload a solidity file or a python file and allows you to visualize the abstract syntax tree both using JSON and graphviz framework. Then uses a Large Language Model (LLM) to describe and interpret the functionality of the code and itemizes its security vulnerabilities


## Authors

- By Ethelbert Uzodinma [@etexaco123](https://www.github.com/etexaco123)


## Procedure
- Create a vitual environment in your local drive
- Download the project from the github repo
- Run `pip install -r requirements.txt`
- In your terminal or command line Run `solc-select install 0.8.0`
- Go to [OPEN AI](https://platform.openai.com/account/api-keys) to obtain your unique API key. 
- Also go to [billing](https://platform.openai.com/account/billing/overview) to add some funds as little as 5 euros to have access to OPEN AI language models, This model is based on **text-davinci-003**. Please ignore this if you already have some funds in your OPEN API account
- After the previous steps, On the **HOME** screen of the application, click on **SignUp** to create a mockup username and password to have access to your own environment.
- Then Click the **Login** button
- To see the AI code interpretation using LLM enter the API key from OPEN AI in the tab and click the toggle button, then wait to see the key activated, then click on **Interpret** to see the interpretation of functionality of the code you uploaded. **Note** other app functionalities work without the the use of API key except for the code interpretation.

  
  
### Below is the HOME screen of the application
  

![Alt](https://github.com/etexaco123/AI_code_analyzer/blob/main/code_analyzer.png?raw=true)
## Demo

The application is already deployed as a web app to the cloud as a minimum viable product and ready to use. Click on this link [here](https://aicodeanalyzer.streamlit.app/) to test the app in production.You can try out the app with my demo API key **Please use an OPENAI API key to access restricted LLM results** . Register with any dummy username and password.


## API Reference

#### Get your open ai key

```http
  GET /api/items
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `api_key` | `string` | **Required**. Your OPEN API key |







