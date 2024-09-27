from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import os  

app = Flask(__name__)

# Kullanıcıdan Username Al
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form["username"].lower()  # Kullanıcı adını küçük harfe çevir
        following, followers = get_follow_data(username)
        difference_list = set(following) - set(followers)
        return render_template("result.html", username=username, difference_list=difference_list)
    return render_template("index.html")

def get_follow_data(username):
    following = []
    followers = []

    def get_users(source, page_name):
        persons = source.find_all("div", attrs={"class": "person-summary"})
        for i in persons:
            if page_name == "following":
                following.append(i.find("h3").find("a")["href"])
            else:
                followers.append(i.find("h3").find("a")["href"])

    def connect_page(page_name):
        page_num = 1
        while True:
            url = f"https://letterboxd.com/{username}/{page_name}/page/{page_num}/"
            source = BeautifulSoup(requests.get(url).content, "lxml")
            if f'<a class="next" href="/{username}/{page_name}/' in str(source):
                get_users(source, page_name)
                page_num += 1
            else:
                get_users(source, page_name)
                break

    for page_name in ("following", "followers"):
        connect_page(page_name)

    return following, followers

if __name__ == "__main__":
    # Flask uygulamasını, ortam değişkenlerinden PORT alarak başlat
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
