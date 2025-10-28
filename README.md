# Restaurant Menu Summarizer

This project scrapes restaurant websites, extracts their daily menus using an LLM, and caches the structured results in a local SQLite database.

## How to Run the Project

### 1) Clone the Repository
```bash
git clone https://github.com/ithinkiminthewronghub/Restaurant-Menu-Summarizer.git
cd Restaurant-Menu-Summarizer/pythonProject1
```

### 2) Set up the environment
```bash
python -m venv venv
source venv/bin/activate  # Ve Windows: venv\Scripts\activate
```

### 3) Install dependencies
```bash
pip install -r requirements.txt
```

### 4) Set up environment variables
Create .env file and add your OpenAI API key and API key (for authentication). It should look like this:
OPENAI_API_KEY=your_openai_api_key
API_KEY=your_api_key

### 5) Run the application
```bash
cd main_logic
python app.py
```

Now you can test my application. I added a simple authentication process, so don't forget to add your API key to Postman 
when trying urls. If daily menu is absent, you can simply pass the link of the menu, and it will still provide you
with the result.

Part of the assignment was to store the results in order to provide the customer with quicker answers in case of repeated
queries. Every restaurant is cleaned from cache every 12 hours. I think it is enough time to store information about one
place. First of all, a person is likely to use the application for lunch and dinner, and 12 hours will cover that. Besides,
in case of daily menu, it will get renewed every day, so 12 hours is enough for that too.

In terms of bonus points, I mentioned the simple authentication. There is also a detection for vegan, vegetarian and
gluten-free dishes, but it is not 100% accurate. If the menu contains allergens, the app will write it in a list, 
and if not, it will tell the customer to ask the staff. There is a detection of holidays, which warns the customer that
the menu might differ. 

## List of links to test on:
* https://www.spojka-karlin.cz/menu
* https://factory.fabrik.cz/menu
* https://www.bistrorepublika.cz/menu
* https://www.zlata-hvezda.cz/jidelni-listek
* https://uvankovky.gourmetrestaurant.cz
* https://ukarlabrno.cz/menu/pages/poledni-menu

## How to Run the Tests

In folder 'tests' you will find a few simple tests to check the flow of the application, the caching implementation and
the parser part.

### 1) Run all tests
```bash
cd tests
pytest -v
```

### 2) Run a specific test
```bash
pytest name_of_test.py
```








