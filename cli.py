"""CLI for interacting with the FoodFast Inventory API."""

import argparse
import json
import sys

import requests

DEFAULT_BASE_URL = "http://127.0.0.1:5000"


def _request(method: str, path: str, base_url: str, **kwargs) -> requests.Response:
    url = f"{base_url.rstrip('/')}{path}"
    return requests.request(method, url, timeout=10, **kwargs)


def _print_json(data) -> None:
    print(json.dumps(data, indent=2))


def _handle_response(response: requests.Response) -> None:
    if response.status_code == 204:
        print("Deleted successfully.")
        return
    try:
        body = response.json()
    except ValueError:
        body = response.text
    if response.ok:
        _print_json(body)
    else:
        print(f"Error ({response.status_code}):", file=sys.stderr)
        _print_json(body)
        sys.exit(1)


def cmd_list(args) -> None:
    _handle_response(_request("GET", "/inventory", args.base_url))


def cmd_show(args) -> None:
    _handle_response(_request("GET", f"/inventory/{args.id}", args.base_url))


def cmd_add(args) -> None:
    payload = {
        "product_name": args.name,
        "brands": args.brands or "",
        "barcode": args.barcode or "",
        "ingredients_text": args.ingredients or "",
        "price": args.price,
        "stock": args.stock,
    }
    _handle_response(
        _request("POST", "/inventory", args.base_url, json=payload)
    )


def cmd_update(args) -> None:
    payload = {}
    if args.price is not None:
        payload["price"] = args.price
    if args.stock is not None:
        payload["stock"] = args.stock
    if args.name is not None:
        payload["product_name"] = args.name
    if not payload:
        print("Nothing to update. Provide --price, --stock, or --name.", file=sys.stderr)
        sys.exit(1)
    _handle_response(
        _request("PATCH", f"/inventory/{args.id}", args.base_url, json=payload)
    )


def cmd_delete(args) -> None:
    _handle_response(_request("DELETE", f"/inventory/{args.id}", args.base_url))


def cmd_find_barcode(args) -> None:
    _handle_response(
        _request("GET", f"/external/product/{args.barcode}", args.base_url)
    )


def cmd_find_name(args) -> None:
    _handle_response(
        _request("GET", "/external/search", args.base_url, params={"name": args.name})
    )


def cmd_import(args) -> None:
    payload = {"price": args.price, "stock": args.stock}
    if args.barcode:
        payload["barcode"] = args.barcode
    elif args.name:
        payload["name"] = args.name
    else:
        print("Provide --barcode or --name.", file=sys.stderr)
        sys.exit(1)
    _handle_response(
        _request("POST", "/inventory/from-api", args.base_url, json=payload)
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="FoodFast Inventory CLI")
    parser.add_argument(
        "--base-url", default=DEFAULT_BASE_URL, help="API base URL"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List all inventory items").set_defaults(func=cmd_list)

    show = sub.add_parser("show", help="Show a single item")
    show.add_argument("id", type=int)
    show.set_defaults(func=cmd_show)

    add = sub.add_parser("add", help="Add a new inventory item")
    add.add_argument("name")
    add.add_argument("--brands", default="")
    add.add_argument("--barcode", default="")
    add.add_argument("--ingredients", default="")
    add.add_argument("--price", type=float, default=0)
    add.add_argument("--stock", type=int, default=0)
    add.set_defaults(func=cmd_add)

    update = sub.add_parser("update", help="Update price, stock, or name")
    update.add_argument("id", type=int)
    update.add_argument("--price", type=float)
    update.add_argument("--stock", type=int)
    update.add_argument("--name")
    update.set_defaults(func=cmd_update)

    delete = sub.add_parser("delete", help="Delete an item")
    delete.add_argument("id", type=int)
    delete.set_defaults(func=cmd_delete)

    barcode = sub.add_parser("find-barcode", help="Look up product on OpenFoodFacts")
    barcode.add_argument("barcode")
    barcode.set_defaults(func=cmd_find_barcode)

    find_name = sub.add_parser("find-name", help="Search OpenFoodFacts by name")
    find_name.add_argument("name")
    find_name.set_defaults(func=cmd_find_name)

    imp = sub.add_parser("import", help="Import product from OpenFoodFacts into inventory")
    imp.add_argument("--barcode", default="")
    imp.add_argument("--name", default="")
    imp.add_argument("--price", type=float, default=0)
    imp.add_argument("--stock", type=int, default=0)
    imp.set_defaults(func=cmd_import)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except requests.ConnectionError:
        print(
            f"Could not connect to API at {args.base_url}. "
            "Start the server with: python app.py",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
