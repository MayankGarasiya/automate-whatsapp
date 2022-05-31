from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient("mongodb+srv://monu:monu@cluster0.srbek.mongodb.net/?retryWrites=true&w=majority")
db = cluster["bakery"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)

@app.route("/", methods=["get", "post"])

def reply():
    text = request.form.get("Body")
    numbers = request.form.get("From")
    numbers= numbers.replace("whatsapp:", "")
    response = MessagingResponse()
    # msg = response.message(f"Thanks for contacting me. you have sent '{text}' from {numbers[:-2]}")
    # msg1 = "Good Morning"
    # msg.media("https://images.unsplash.com/photo-1616879577377-ca82803b8c8c?ixlib=rb-1.2.1&raw_url=true&q=60&fm=jpg&crop=entropy&cs=tinysrgb&ixid=MnwxMjA3fDB8MHxjb2xsZWN0aW9uLXBhZ2V8MXwxMTcyNjIyfHxlbnwwfHx8fA%3D%3D&auto=format&fit=crop&w=500")

    user = users.find_one({"number": numbers})
    if bool(user) == False:
        response.message("Hi, thanks for contacting *The Red velvet* \nYou can choose frome one of the options below: "
                         "\n\n*Type*\n\n 1️⃣ To  *contact* us \n 2️⃣ To *order* snacks \n 3️⃣ To know our *working hours* \n 4️⃣"
                         "To get our *address*")
        users.insert_one({"number": numbers, "status": "main", "messages": []})
    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            response.message("please enter a valid response")
            return str(response)
        if option == 1:
            response.message("You can contact us through phone or email.\n\n*Phone*:9925616724 \n*E-mail* :contact@welspun.com")
        elif option == 2:
            response.message("You have entered *ordering mode*.")
            users.update_one({"number": numbers}, {"$set": {"status":"ordering"}})
            response.message("You can select one of the following cake to order: \n\n1️⃣ Red velvet \n2️⃣ Dark Forest \n3️⃣ Ice Cream Cake"
                             "\n4️⃣ Plum Cake \n5️⃣ Sponge Cake \n6️⃣ Genoise Cake \n7️⃣ Angel Cake \n8️⃣ Carrot Cake \n9️⃣ Fruit Cake \n0️⃣ Go Bake")
        elif option == 3:
            response.message("We worked everyday from *9 a.m to 5 p.m*")
        elif option == 4:
            response.message("Ahmedabad")
        else:
            response.message("please enter a valid response")

    elif user["status"] == "ordering":
        try:
            option = int(text)
        except:
            response.message("please enter a valid response")
            return str(response)
        if option == 0:
            users.update_one(
                {"number": numbers},{"$set": {"status": "main"}})
            response.message("You can choose frome one of the options below: "
                         "\n\n*Type*\n\n 1️⃣ To  *contact* us \n 2️⃣ To *order* snacks \n 3️⃣ To know our *working hours* \n 4️⃣"
                         "To get our *address*")
        elif 1<= option <=9:
            cakes = ["Red Velvet Cake", "Dark Forest Cake", "Ice cream Cake",
                     "Plum Cake", "Sponge Cake", "Genoise Cake","Angel Cake", "Carrot Cake", "Fruit Cake"]
            selected = cakes[option - 1]
            users.update_one(
                {"number": numbers}, {"$set": {"status": "address"}})
            users.update_one(
                {"number": numbers}, {"$set": {"item": selected}})
            response.message("Excellent Choice 🤗")
            response.message("Please Enter your *address* to confirm the order")
        else:
            response.message("please enter a valid response")

    elif user["status"] == "address":
        selected = user["item"]
        response.message("Thanks for shopping with us!")
        response.message(f"Your order for {selected} has been recieved and will be delivered within an hour")
        orders.insert_one({"number": numbers, "item": selected, "address": text, "order_time":datetime.now()})
        users.update_one(
            {"number": numbers}, {"$set": {"status": "ordered"}})
    elif user["status"] == "ordered":
        response.message("Hi, thanks for contacting again. \nYou can choose frome one of the options below: "
                         "\n\n*Type*\n\n 1️⃣ To  *contact* us \n 2️⃣ To *order* snacks \n 3️⃣ To know our *working hours* \n 4️⃣"
                         "To get our *address*")
        users.update_one(
            {"number": numbers}, {"$set": {"status": "main"}})

    # else:
    #     # response.message("You can choose frome one of the options below: "
    #     #                  "\n\n*Type*\n\n 1️⃣ To  *contact* us \n 2️⃣ To *order* snacks \n 3️⃣ To know our *working hours* \n 4️⃣"
    #     #                  "To get our *address*")

    users.update_one({"number": numbers}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})
    return str(response)


if __name__ == "__main__":
    app.run()
