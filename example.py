#!/usr/bin/env python
# -*- coding:utf-8 -*-


from dnspod import apicn
import requests
import socket
import json
import time


def get_ip():
    rsp = requests.get("http://ip.sb", headers={'user-agent': 'curl/2.33'})
    ip = rsp.text.strip()
    try:
        socket.inet_aton(ip)
    except socket.error:
        print("invalid response from ip.sb", rsp.text)
        return None
    return ip


def update(login_token, domain, subdomain, new_ip):
    api = apicn.DomainId(domain=domain, login_token=login_token)
    domains = api()
    domain_id = domains.get("domains").get("id")
    api = apicn.RecordList(domain_id, login_token=login_token)
    recs = api().get("records")
    found = False
    for rec in recs:
        if rec.get("type") == "A" and rec.get("name") == subdomain:
            found = True
            break
    if not found:
        print "Record not found; available records:", recs
    if rec.get("value").strip() == new_ip:
        print "IP is up to date"
        return
    record_id = rec.get("id")
    record_line = rec.get("line") 
    api = apicn.RecordModify(
        record_id, sub_domain=subdomain, record_type="A", record_line=record_line,
        value=new_ip, ttl=600,
        domain_id=domain_id, login_token=login_token)
    try:
        ret = api()
        print "Success", ret
    except apicn.DNSPodApiException as e:
        print(e)
        return False


def main():
    with open('config.json', 'r') as f:
        cfg = json.load(f)

    last_ip = None
    while True:
        ip = get_ip()
        if ip is not None and ip != last_ip:
            print "Updating: ", last_ip, "->", ip
            update(cfg['login_token'], cfg['domain'], cfg['subdomain'], ip)
            last_ip = ip
        time.sleep(600)

if __name__ == '__main__':
    main()
