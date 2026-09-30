"""Generates docs/architecture.drawio for the Student Learning Assistant project using drawpyo.

Run with: python3 scripts/generate_diagram.py
"""
import os

import drawpyo

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")

AWS4_BASE = (
    "sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=none;"
    "dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;"
    "fontSize=11;fontStyle=0;aspect=fixed;pointerEvents=1;"
)


def aws_style(icon_name, fill_color):
    return f"{AWS4_BASE}fillColor={fill_color};shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.{icon_name};"


def add_node(page, name, x, y, icon_name, fill_color, width=64, height=64):
    node = drawpyo.diagram.Object(page=page, value=name)
    node.position = (x, y)
    node.geometry.width = width
    node.geometry.height = height
    node.apply_style_string(aws_style(icon_name, fill_color))
    return node


def add_edge(page, source, target, label=None, bidirectional=False):
    edge = drawpyo.diagram.Edge(page=page, source=source, target=target, label=label)
    edge.waypoints = "orthogonal"
    edge.endArrow = "block"
    edge.startArrow = "block" if bidirectional else "none"
    edge.strokeColor = "#545B64"
    return edge


def build_diagram():
    file = drawpyo.File()
    file.file_name = "architecture.drawio"
    file.file_path = OUTPUT_DIR

    page = drawpyo.Page(file=file)
    page.name = "Student Learning Assistant"

    device = add_node(page, "Teachers and\nstudents", 40, 220, "client", "#232F3E")
    alb = add_node(page, "Traffic\ndistribution", 240, 220, "application_load_balancer", "#8C4FFF")
    app_service = add_node(page, "Containerized\napplication", 440, 220, "ecs", "#ED7100")

    qa_table = add_node(page, "Q&A and scores\ntables", 440, 40, "dynamodb", "#C925D1")
    images_bucket = add_node(page, "Generated\nimages", 660, 40, "bucket", "#7AA116")
    bedrock_models = add_node(page, "Create assignments\nand images", 660, 220, "machine_learning", "#01A88D")

    add_edge(page, device, alb, "Subject / Assignment", bidirectional=True)
    add_edge(page, alb, app_service, "Access application / Score and feedback", bidirectional=True)
    add_edge(page, app_service, qa_table, "Save Q&A / Get Q&A", bidirectional=True)
    add_edge(page, app_service, bedrock_models, "Query Q&A, image / Score and feedback", bidirectional=True)
    add_edge(page, bedrock_models, images_bucket, "Save image / Get image", bidirectional=True)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file.write()
    print(f"Wrote {os.path.join(OUTPUT_DIR, file.file_name)}")


if __name__ == "__main__":
    build_diagram()
