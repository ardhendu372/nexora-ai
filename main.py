
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    temperature=0.2
)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are Nexora AI, a friendly AI assistant.

        Follow these rules:
        1. Give simple and clear answers.
        2. Explain technical topics with examples.
        3. Help beginners understand programming.
        4. Use a friendly and professional tone.
        5. If you don't know something, say so honestly.
        """
    ),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}")
])

chain = prompt | llm

print("Welcome to Nexora AI!")
print("Type 'exit' to stop the chatbot.")

chat_history = []

while True:
    question = input("\nYou: ")

    if not question.strip():
        print("Nexora AI: Please enter a question.")
        continue

    if question.lower() == "exit":
        print("Nexora AI: Goodbye!")
        break

    try:
        print("\nNexora AI: Thinking...")

        response = chain.invoke({
            "chat_history": chat_history,
            "question": question
        })

        chat_history.append(HumanMessage(content=question))
        chat_history.append(AIMessage(content=response.text))

        print("\nNexora AI:", response.text)

    except Exception as e:
        print("\nNexora AI: Something went wrong. Please try again.")
        print("Error:", e)
