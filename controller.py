#!/usr/bin/python3
import os
import model
import tkinter
import urllib.parse 
import requests
from io import BytesIO
from PIL import Image, ImageTk

class mkm_seller_controller():
    
    def __init__(self):
        self.mkm_seller_model = model.mkm_seller_model()

    def populate_card_tree(self, tree):
        # titles = ("set", "condition", "language", "price", "extra", "number")
        data = self.mkm_seller_model.load_csv()
        for i, card in enumerate(data):
            values = (card["set"], card["condition"], card["language"], "", card["extra"], card["number"])
            tree.insert("", "end", text=card["name"], values=values)
        
        return True
        
    def show_card_details(self, tree, label_image):
        item = tree.selection()[0]
        print("you clicked on", tree.item(item,"values"))
        label_image.winfo_children()
        for child in label_image.winfo_children():
            child.config()
        # lang_dict = {"vo": 1, "vf": 2}
        # card_name = tree.item(item,"text")
        # print(card_name)
        # lang = tree.item(item,"values")[2]
        # mkm_request = self.mkm_seller_model.get_products_by_name(card_name, idLanguage=2)
        # if mkm_request:
            # card = mkm_request["product"][0]
        # else:
            # print("KO")
            # return False
        # url = urllib.parse.urljoin("https://www.cardmarket.com/", card["image"])
        # print(url)
        # response = requests.get(url)
        # im = Image.open(BytesIO(response.content))
        # img = ImageTk.PhotoImage(im)
        # label_image.configure(image=img)
        # label_image.image = img
        
        
    def gif_convert(self):
        img_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "card.jpg")
        im = Image.open(img_path)

        im = im.convert('RGB').convert('P', palette=Image.ADAPTIVE)
        img_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "card.gif")
        im.save(img_path)
        