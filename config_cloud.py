from datetime import datetime, timedelta
from os import path
from typing import List

import toml

from const import downloads_dir
from data_struct import ConfigInterface
from download import download_github_raw_content
from first_run import is_first_run_in
from log import color, logger
from update import version_less
from util import async_call, parse_time, try_except


class BlackListConfig(ConfigInterface):
    def __init__(self):
        # 封禁于
        self.ban_at = "2020-01-01"
        # QQ
        self.qq = ""
        # 昵称
        self.nickname = ""
        # 原因
        self.reason = ""


class TryAutoUpdateIgnorePermissionConfig(ConfigInterface):
    def __init__(self):
        # 最新已修复bug的版本。当填写该值后，早于该版本的小助手可无视权限触发dlc
        self.latest_bug_fixed_version = ""
        # 指定时间段内可无视权限触发dlc
        self.period_list: list[tuple[str, str]] = []

    def can_ignore(self, current_version: str, now: datetime) -> bool:
        if self.latest_bug_fixed_version != "" and version_less(current_version, self.latest_bug_fixed_version):
            logger.info(color("bold_yellow") + f"当前版本为 {current_version}, 低于最新修复bug版本 {self.latest_bug_fixed_version}，可无视权限触发dlc")
            return True

        for str_begin, str_end in self.period_list:
            begin, end = parse_time(str_begin), parse_time(str_end)
            if begin <= now <= end:
                logger.info(color("bold_yellow") + f"当前时间为 {now}, 在指定时间段内[{begin}, {end}]，可无视权限触发dlc")
                return True

        return False


class ChromeVersionReplaceRule(ConfigInterface):
    def __init__(self):
        # 有问题的chrome大版本列表，如110版本在部分win7电脑上无法正常使用
        self.troublesome_major_version_list: list[int] = []
        # 用于替换的可用chrome大版本
        self.valid_chrome_version: int = 0


# 远程配置，方便动态调整部分配置
class ConfigCloud(ConfigInterface):
    def __init__(self):
        # 是否已经从配置文件中加载
        self.loaded = False

        # 新增的服务器IP列表
        self.server_ip_list: List[str] = []

        # 是否启用卡密界面
        self.enable_card_secret = True
        # 是否启用直接购买界面
        self.enable_pay_directly = True
        # 是否优先展示卡密界面
        self.show_card_secret_first = False

        # 是否显示支付宝红包图片
        self.enable_alipay_redpacket = False

        # 新增的黑名单
        self.black_list: List[BlackListConfig] = []

        # dlc是否优先启用alist
        self.dlc_prefer_alist = False

        # 是否启用推荐奖励
        self.enable_recommend_reward = True

        # 无视权限进行自动更新的条件
        self.try_auto_update_ignore_permission = TryAutoUpdateIgnorePermissionConfig()

        # chrome版本强制更换，用于处理新升级chrome后，部分电脑上无法正常使用的情况下可以远程降级为可用的其他版本，在新版本发布前减少影响
        self.chrome_version_replace_rule = ChromeVersionReplaceRule()

    def fields_to_fill(self):
        return [
            ("black_list", BlackListConfig),
        ]


# 配置保存路径
save_dir = downloads_dir
# 配置文件名
cloud_config_filename = "config.cloud.toml"

g_config_cloud = ConfigCloud()


# 获取远程配置，首次调用时会触发加载
def config_cloud() -> ConfigCloud:
    if not g_config_cloud.loaded:
        load_config_cloud()

    return g_config_cloud


# 读取远程config
def load_config_cloud():
    global g_config_cloud

    # 尝试读取远程配置
    try:
        raw_config = toml.load(path.join(save_dir, cloud_config_filename))
        g_config_cloud.auto_update_config(raw_config)
    except Exception as e:
        logger.debug("读取远程配置失败", exc_info=e)

    async_update_config_cloud()

    # 标记为已经初始化完毕
    g_config_cloud.loaded = True


@try_except()
def async_update_config_cloud():
    if not is_first_run_in("同步远程配置", timedelta(minutes=10)):
        return

    logger.info("尝试异步从github下载最新的远程配置，供下次读取使用（主要是为了避免影响其他流程）")
    async_call(download_github_raw_content, cloud_config_filename, save_dir)


if __name__ == "__main__":
    load_config_cloud()
    logger.info(f"{g_config_cloud}")

    from util import pause

    pause()
