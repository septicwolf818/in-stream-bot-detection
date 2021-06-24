"""Event generator for In-Stream processing project
"""
import datetime
import math
import random
import json
import argparse


class Events():
    def __init__(self, ip):
        """Base events class

        Args:
            ip (str): IP for events to be generated
        """
        self.ip = ip
        self.start_time = datetime.datetime.utcnow()
        self.current_time = self.start_time
        self.min_events = 1
        self.max_events = 1

    def generate_events(self):
        """Event generation method

        Returns:
            list: List of generated events for given IP
        """
        events = []
        event_count = random.randint(self.min_events, self.max_events)
        event_rate = math.ceil(event_count / 10)
        activity_time = math.ceil(event_count/event_rate)
        for _ in range(activity_time):
            for _ in range(event_rate):
                if(len(events) == event_count):
                    break
                events.append(
                    json.dumps({
                        "type": random.choice(["click", "view"]),
                        "ip": self.ip,
                        "event_time": str(
                            int(self.current_time.timestamp())),
                        "url": random.choice(
                            ["example.com", "example.net", "example.org"]) +
                        "/" +
                        random.choice(["search-results", "blog", "page"]) +
                        "/" +
                        random.choice([str(random.randint(1, 10))])}))
            self.current_time += datetime.timedelta(seconds=1)
        return events


class UserEvents(Events):
    def __init__(self, ip):
        """User events class

        Args:
            ip (str): IP for events to be generated
        """
        super().__init__(ip)
        self.min_events = 1
        self.max_events = 20


class BotEvents(Events):
    def __init__(self, ip):
        """Bot events class

        Args:
            ip (str): IP for events to be generated
        """
        super().__init__(ip)
        self.min_events = 21
        self.max_events = 40


def main():
    parser = argparse.ArgumentParser(description='Event generator')
    parser.add_argument('-u', '--users', help='user count',
                        default=1, type=int, metavar="users", required=False)
    parser.add_argument('-b', '--bots', help='bot count',
                        default=1, type=int, metavar="bots", required=False)
    events = []
    err = False
    args = parser.parse_args()
    if args.users > 65534 or args.bots > 65534:
        print(json.dumps(
            {"error": "Unable to generate more than 65534 IPs for /16 netmask"}))
        err = True
    elif args.users < 0 or args.bots < 0:
        print(json.dumps(
            {"error": "Parameters can not be negative"}))
        err = True
    if not err:
        # User IPs 172.0.0.0/16
        # Bot IPs 172.8.0.0/16
        user_ips = [str("172.0." + str(int(n/256)) + "." + str(n % 256))
                    for n in range(1, args.users+1)]
        bot_ips = [str("172.8." + str(int(n/256)) + "." + str(n % 256))
                   for n in range(1, args.bots+1)]
        random.shuffle(user_ips)
        random.shuffle(bot_ips)

        for x in user_ips:
            for event in UserEvents(x).generate_events():
                events.append(event)
                print(event)

        for x in bot_ips:
            for event in BotEvents(x).generate_events():
                events.append(event)
                print(event)
        
        return events


if __name__ == "__main__":
    main()
