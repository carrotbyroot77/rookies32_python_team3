from flask import Flask, render_template, request
from datetime import datetime

from oil_api import get_avg_oil_price, get_low_top20
from config import AREAS, PRODUCTS

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    try:
        prodcd = request.args.get("prodcd", "B027")
        area = request.args.get("area", "")

        avg_list = get_avg_oil_price()
        low_top20_list = get_low_top20(prodcd, area)

        update_time = datetime.now().strftime("%Y-%m-%d %H:%M")

        return render_template(
            "index.html",
            avg_list=avg_list,
            low_top20_list=low_top20_list,
            selected_prodcd=prodcd,
            selected_area=area,
            areas=AREAS,
            prod_list=PRODUCTS,
            update_time=update_time
        )

    except Exception as e:
        return f"에러 발생 : {e}"


if __name__ == "__main__":
    app.run(debug=True)