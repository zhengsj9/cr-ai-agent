
import csv

# 1. 定义商品分类规则

CATEGORY_RULES = {
    "Pet Supplies": [
        "dog", "cat", "pet", "grooming"
    ],

    "Sports & Outdoors": [
        "camping", "hiking", "trekking",
        "yoga", "fitness", "cycling",
        "running", "sports", "sleeping bag",
        "water bottle", "headlamp",
        "tent", "camping stove",
        "camping chair", "dry bag",
        "binoculars"
    ],

    "Travel": [
        "travel", "luggage", "backpack",
        "packing cubes", "travel wallet",
        "neck pillow", "luggage scale",
        "travel umbrella"
    ],

    "Office Supplies": [
        "office", "desk", "document scanner",
        "label maker", "whiteboard",
        "book stand", "bookends",
        "receipt printer", "book light",
        "document"
    ],

    "Garden & Outdoor": [
        "garden", "pruning", "hose nozzle",
        "herb garden", "solar garden",
        "string lights"
    ],

    "Health & Personal Care": [
        "first aid", "toothbrush",
        "face masks", "thermometer",
        "heating pad", "compression socks"
    ],

    "Toys & Crafts": [
        "building blocks", "board game",
        "puzzle", "acrylic paint",
        "sketching", "watercolor",
        "craft cutting"
    ],

    "Tools & Hardware": [
        "tool kit", "tire inflator",
        "surge protector"
    ],

    "Home & Kitchen": [
        "kitchen", "coffee", "cookware",
        "vacuum", "curtain", "pillow",
        "blanket", "air fryer",
        "food scale", "milk frother",
        "food storage", "baking mat",
        "humidifier", "fan",
        "alarm clock", "storage basket",
        "cleaning cloth", "shower curtain",
        "lunch bag", "lunch thermos",
        "food containers"
    ],

    "Electronics": [
        "bluetooth", "wireless",
        "camera", "monitor", "keyboard",
        "mouse", "projector", "webcam",
        "charger", "computer",
        "smart plug", "led light bulb",
        "ssd", "solid state drive",
        "docking station", "hdmi",
        "wi-fi", "wifi",
        "power bank", "charging pad",
        "receipt printer", "digital clock"
    ]
}


# 2. 根据商品信息判断分类
def classify_product(product):

    text = (
        product["name"] + " " +
        product["features"]
    ).lower()

    for category, keywords in CATEGORY_RULES.items():

        for keyword in keywords:

            if keyword in text:
                return category

    return "Other"


# 3. 读取原始 CSV
products = []

with open(
    "products.csv",
    "r",
    encoding="utf-8-sig",
    newline=""
) as file:

    reader = csv.DictReader(file)

    for row in reader:
        products.append(row)


# 4. 增加 category 字段
for product in products:

    product["category"] = classify_product(product)


# 5. 保存新的 CSV
fieldnames = [
    "product_id",
    "name",
    "market",
    "features",
    "category"
]

with open(
    "products_with_category.csv",
    "w",
    encoding="utf-8-sig",
    newline=""
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(products)


# 6. 输出分类统计
print("\n========== 商品分类结果 ==========")

category_count = {}

for product in products:

    category = product["category"]

    category_count[category] = (
        category_count.get(category, 0) + 1
    )

for category, count in category_count.items():

    print(category, ":", count)

# 7. 输出分类诊断信息

print("\n========== 分类规则检查 ==========")

print("当前分类规则数量：", len(CATEGORY_RULES))

print("当前分类名称：")

for category in CATEGORY_RULES:
    print("-", category)

print("\n========== Other 商品检查 ==========")

for product in products:

    if product["category"] == "Other":

        print(
            product["product_id"],
            product["name"]
        )

print("\n商品总数：", len(products))
print("分类数据保存成功！")