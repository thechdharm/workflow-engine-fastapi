from app.db import SessionLocal, init_db
from app.models import Workflow
from app.utils import gen_id

def seed():
    init_db()
    db = SessionLocal()

    # Scenario 1: Lead Routing
    graph1 = {
        "nodes": [
            {"id": "start", "type": "start", "data": {}},
            {"id": "n1", "type": "send_notification", "data": {"toRole": "AE", "message": "New hot lead"}},
            {"id": "n2", "type": "delay", "data": {"ms": 24*60*60*1000}},
            {"id": "n3", "type": "http_call", "data": {"method": "POST", "url": "https://httpbin.org/post", "body": {"templateId": "followup_1", "lead": "{{payload.lead.title}}"}}},
            {"id": "br1", "type": "branch", "data": {"cases": [
                {"label": "CEO", "condition": {"and": [ { "==": [ {"var": "lead.title"}, "CEO" ] } ]}, "next": "gift_start"},
                {"label": "else", "else": True, "next": "drip_start"}
            ]}},
            {"id": "gift_start", "type": "send_notification", "data": {"toRole": "AE", "message": "Trigger gifting sequence"}},
            {"id": "drip_start", "type": "send_notification", "data": {"toRole": "AE", "message": "Trigger drip campaign"}}
        ],
        "edges": [
            {"id": "e1", "source": "start", "target": "n1"},
            {"id": "e2", "source": "n1", "target": "n2"},
            {"id": "e3", "source": "n2", "target": "n3"},
            {"id": "e4", "source": "n3", "target": "br1"}
        ]
    }
    trigger1 = {"and":[ { "==": [ {"var":"lead.source"}, "LinkedIn" ] }, { ">": [ {"var":"lead.score"}, 75 ] } ]}

    wf1 = Workflow(id=gen_id(), name="Lead routing", trigger=trigger1, graph=graph1, definition=graph1, is_active=True)
    db.add(wf1)

    # Scenario 2: Temperature Control
    graph2 = {
        "nodes": [
            {"id": "start", "type": "start", "data": {}},
            {"id": "t1", "type": "http_call", "data": {"method": "POST", "url": "https://httpbin.org/post", "body": {"action": "AC_ON"}}},
            {"id": "t2", "type": "delay", "data": {"ms": 5*60*1000}},
            {"id": "t3", "type": "branch", "data": {"cases": [
                {"label": "still_hot", "condition": {">":[ {"var":"temp"}, 30 ]}, "next": "t3_notify"},
                {"label": "cooled", "else": True, "next": "end"}
            ]}},
            {"id": "t3_notify", "type": "send_notification", "data": {"toRole": "manager", "message": "Temperature still high"}},
            {"id": "t4_delay_ack", "type": "delay", "data": {"ms": 10*60*1000}},
            {"id": "t5_branch_ack", "type": "branch", "data": {"cases": [
                {"label": "ack", "condition": {"==":[ {"var":"manager_ack"}, True ]}, "next": "end"},
                {"label": "else", "else": True, "next": "t5_backup"}
            ]}},
            {"id": "t5_backup", "type": "http_call", "data": {"method": "POST", "url": "https://httpbin.org/post", "body": {"action": "BACKUP_COOLING"}}},
            {"id": "end", "type": "end", "data": {}}
        ],
        "edges": [
            {"id": "e1", "source": "start", "target": "t1"},
            {"id": "e2", "source": "t1", "target": "t2"},
            {"id": "e3", "source": "t2", "target": "t3"},
            {"id": "e4", "source": "t3", "target": "t3_notify"},
            {"id": "e5", "source": "t3_notify", "target": "t4_delay_ack"},
            {"id": "e6", "source": "t4_delay_ack", "target": "t5_branch_ack"},
            {"id": "e7", "source": "t5_branch_ack", "target": "t5_backup"}
        ]
    }
    trigger2 = {">": [ {"var":"temp"}, 30 ]}
    wf2 = Workflow(id=gen_id(), name="Temperature control", trigger=trigger2, graph=graph2, definition=graph2, is_active=True)
    db.add(wf2)

    db.commit()
    print("Seeded 2 workflows.")

if __name__ == "__main__":
    seed()
