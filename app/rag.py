
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

def get_summary(user_name , data):
    chat = ChatGroq(temperature=0, groq_api_key=API_KEY, model_name="llama3-70b-8192",  api_key="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" )
   

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                You are a helpful assistant tasked with providing a detailed work progress summary for the user with the name '{user_name}'.
                Your goal is to analyze and summarize the user's work feedback.

                Weekly Data : `{user_data}`

                Instructions:
                1. Start by providing a brief overview of the user's overall performance for the week.
                2. Create a list of bullet points highlighting key achievements, challenges faced, and areas for improvement.
                3. Ensure each bullet point is specific, descriptive, and actionable.
                4. Maintain a professional and supportive tone throughout the summary.

                

                Output:
                - use user's name for refrence.
                - Provide the detailed summary and use the data provided.
                - Ensure the summary is concise and provides useful insights.

                """,
            ),
            ("human", "{input}"),
        ]
    )

    chain = prompt | chat
    result = chain.invoke(
        {
            "user_name": {user_name},
            "user_data": {data},
            "input": "Provide Summary",
        }
    )
    return result.content


# user_data = """
# Monday:
# did yesterday : Completed initial project design, reviewed team's code submissions.
# doing today : Finalizing the project design, starting the integration of new API.
# blockers faced: Encountered issues with API documentation clarity.

# Tuesday:
# did yesterday : Finalized project design, began integrating new API.
# doing today : Continue API integration, begin writing unit tests for new features.
# blockers faced: Faced challenges with API response handling.

# Wednesday:
# did yesterday : Continued API integration, wrote initial set of unit tests.
# doing today : Complete API integration, expand unit tests, review team's progress.
# blockers faced: API response times are slower than expected, causing delays.

# Thursday:
# did yesterday : Completed API integration, expanded unit tests, reviewed team’s work.
# doing today : Start implementing user interface changes based on new API.
# blockers faced: Design inconsistencies found in user interface elements.

# Friday:
# did yesterday : Implemented user interface changes, fixed design inconsistencies.
# doing today : Conduct end-to-end testing, prepare for deployment.
# blockers faced: Found a critical bug during testing that needs urgent fixing.

# Saturday:
# did yesterday : Conducted end-to-end testing, fixed critical bugs.
# doing today : Finalize deployment preparations, ensure all tests pass.
# blockers faced: Deployment environment setup issues causing delays.

# Sunday:
# did yesterday : Finalized deployment preparations, ensured all tests passed.
# doing today : Deploy the project, monitor post-deployment issues.
# blockers faced: Minor post-deployment issues with user access permissions.


# """

# print(get_summary("nauman", user_data))


