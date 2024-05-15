from xing.core.BaseThread import BaseThread
from xing.utils import get_logger
from xing.utils.save_result import save_result
logger = get_logger()


class BruteRunner(BaseThread):
    def __init__(self, plg,  target, username_list, password_list, concurrency=6):
        auth_list = list(zip(username_list, password_list))
        super(BruteRunner, self).__init__(targets=auth_list, concurrency=concurrency)
        self.plg = plg
        self.target = target
        self.result_map = {}
        self.shuffle_targets = getattr(self.plg, "shuffle_auth_list", False)

    def work(self, auth_pair):
        from xing.core.BasePlugin import BasePlugin
        user, pwd = auth_pair
        if not isinstance(self.plg, BasePlugin):
            return

        if self.result_map.get(user):
            logger.debug("password is founded , skip {}".format(user))
            return

        result = self.plg.login(self.target, user=user, passwd=pwd)
        if result:
            logger.success("found weak pass {}:{} {}".format(user, pwd, self.target))
            msg = "{}----{}:{}".format(self.target, user, pwd)
            save_result(self.plg, msg)
            self.result_map[user] = pwd

    def run(self):
        self._run()
        return self.result_map


def brute_runner(plg,  target, username_list, password_list, concurrency=6):
    runner = BruteRunner(plg=plg, target=target,
                         username_list=username_list, password_list=password_list, concurrency=concurrency)

    return runner.run()