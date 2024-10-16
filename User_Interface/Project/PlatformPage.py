import os
import json
import copy
import random
from functools import partial

from PyQt5.Qt import Qt
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QVBoxLayout

from qfluentwidgets import Action
from qfluentwidgets import InfoBar
from qfluentwidgets import InfoBarPosition
from qfluentwidgets import RoundMenu
from qfluentwidgets import FluentIcon
from qfluentwidgets import PrimaryPushButton
from qfluentwidgets import PrimaryDropDownPushButton

from AiNieeBase import AiNieeBase
from Widget.FlowCard import FlowCard
from Widget.LineEditMessageBox import LineEditMessageBox
from User_Interface.Project.APIEditPage import APIEditPage

class PlatformPage(QFrame, AiNieeBase):

    CUSTOM = {
        "tag": "",
        "group": "custom",
        "name": "",
        "api_url": "",
        "api_key": "",
        "api_format": "",
        "model": "",
        "proxy": "",
        "account": "",
        "auto_complete": True,
        "model_datas": [
            "gpt-4o",
            "gpt-4o-mini",
            "claude-3-5-sonnet-20240620",
        ],
        "format_datas": [
            "OpenAI",
            "Anthropic",
        ],
        "account_datas": {},
        "key_in_settings": [
            "api_url",
            "api_key",
            "api_format",
            "model",
            "proxy",
            "auto_complete",
        ],
    }

    DEFAULT = {}

    def __init__(self, text: str, window, background_executor = None):
        QFrame.__init__(self, window)
        AiNieeBase.__init__(self)
        self.setObjectName(text.replace(" ", "-"))
        
        # 全局窗口对象
        self.window = window

        # 配置文件管理器
        self.background_executor = background_executor

        # 加载默认配置
        self.DEFAULT = self.load_file("./Resource/platforms.json")
        self.save_config(self.load_config_from_default())
    
        # 载入配置文件
        config = self.load_config()

        # 设置主容器
        self.container = QVBoxLayout(self)
        self.container.setSpacing(8)
        self.container.setContentsMargins(24, 24, 24, 24) # 左、上、右、下

        # 添加控件
        self.add_head_widget(self.container, config)
        self.add_body_widget(self.container, config)
        self.add_foot_widget(self.container, config)

        # 填充
        self.container.addStretch(1)

    # 从文件加载
    def load_file(self, path: str) -> dict:
        result = {}

        if os.path.exists(path):
            with open(path, "r", encoding = "utf-8") as reader:
                result = json.load(reader)
        else:
            self.error("未找到 platforms.json 文件 ...")

        return result

    # 执行接口测试
    def api_test(self, tag: str):
        # 载入配置文件
        config = self.load_config()
        platform = config.get("platforms").get(tag)

        if self.background_executor.Request_test_switch(self):
            def callback(result):
                if result == True:
                    InfoBar.success(
                        title = "",
                        content = "接口测试成功 ...",
                        parent = self,
                        duration = 2500,
                        orient = Qt.Horizontal,
                        position = InfoBarPosition.TOP,
                        isClosable = True,
                    )
                else:
                    InfoBar.error(
                        title = "",
                        content = "接口测试失败 ...",
                        parent = self,
                        duration = 2500,
                        orient = Qt.Horizontal,
                        position = InfoBarPosition.TOP,
                        isClosable = True,
                    )
                    
            self.background_executor(
                "接口测试",
                "",
                "",
                tag = platform.get("tag"),
                api_url = platform.get("api_url"),
                api_key = platform.get("api_key"),
                api_format = platform.get("api_format"),
                model = platform.get("model"),
                proxy = platform.get("proxy"),
                auto_complete = platform.get("auto_complete"),
                callback = callback,
            ).start()
        else:
            InfoBar.warning(
                title = "",
                content = "接口测试正在执行中，请稍后再试 ...",
                parent = self,
                duration = 2500,
                orient = Qt.Horizontal,
                position = InfoBarPosition.TOP,
                isClosable = True,
            )

    # 删除平台
    def delete_platform(self, tag: str) -> None:
        # 载入配置文件
        config = self.load_config()
        
        # 删除对应的平台
        del config["platforms"][tag]

        # 保存配置文件
        self.save_config(config)

        # 更新控件
        self.update_custom_platform_widgets(self.flow_card)

    # 生成 UI 描述数据
    def generate_ui_datas(self, platforms: dict, is_custom: bool) -> list:
        ui_datas = []
        
        for k, v in platforms.items():
            if not is_custom:
                ui_datas.append(
                    {
                        "name": v.get("name"),
                        "menus": [
                            (
                                FluentIcon.EDIT,
                                "编辑接口",
                                partial(self.show_api_edit_message_box, k),
                            ),
                            (
                                FluentIcon.SEND,
                                "测试接口",
                                partial(self.api_test, k),
                            ),
                        ],
                    },
                )
            else:
                ui_datas.append(
                    {
                        "name": v.get("name"),
                        "menus": [
                            (
                                FluentIcon.EDIT,
                                "编辑接口",
                                partial(self.show_api_edit_message_box, k),
                            ),
                            (
                                FluentIcon.SEND,
                                "测试接口",
                                partial(self.api_test, k),
                            ),
                            (
                                FluentIcon.DELETE,
                                "删除接口",
                                partial(self.delete_platform, k),
                            ),
                        ],
                    },
                )

        return ui_datas

    # 显示 API 编辑对话框
    def show_api_edit_message_box(self, key: str):
        api_edit_message_box = APIEditPage(self.window, key)
        api_edit_message_box.exec()

    # 初始化下拉按钮
    def init_drop_down_push_button(self, widget, datas):
        for item in datas:
            drop_down_push_button = PrimaryDropDownPushButton(item.get("name"))
            drop_down_push_button.setFixedWidth(192)
            drop_down_push_button.setContentsMargins(4, 0, 4, 0) # 左、上、右、下
            widget.add_widget(drop_down_push_button)

            menu = RoundMenu(drop_down_push_button)
            for k, v in enumerate(item.get("menus")):
                menu.addAction(
                    Action(
                        v[0],
                        v[1],
                        triggered = v[2],
                    )
                )

                # 最后一个菜单不加分割线
                menu.addSeparator() if k != len(item.get("menus")) - 1 else None
            drop_down_push_button.setMenu(menu)

    # 更新自定义平台控件
    def update_custom_platform_widgets(self, widget):
        config = self.load_config()
        platforms = {k:v for k, v in config.get("platforms").items() if v.get("group") == "custom"}

        widget.take_all_widgets()
        self.init_drop_down_push_button(
            widget,
            self.generate_ui_datas(platforms, True)
        )

    # 添加头部
    def add_head_widget(self, parent, config):
        platforms = {k:v for k, v in config.get("platforms").items() if v.get("group") == "local"}
        parent.addWidget(
            FlowCard(
                "本地接口", 
                "管理应用内置的本地大语言模型的接口信息",
                init = lambda widget: self.init_drop_down_push_button(
                    widget,
                    self.generate_ui_datas(platforms, False),
                ),
            )
        )

    # 添加主体
    def add_body_widget(self, parent, config):
        platforms = {k:v for k, v in config.get("platforms").items() if v.get("group") == "online"}
        parent.addWidget(
            FlowCard(
                "在线接口", 
                "管理应用内置的主流大语言模型的接口信息",
                init = lambda widget: self.init_drop_down_push_button(
                    widget,
                    self.generate_ui_datas(platforms, False),
                ),
            )
        )

    # 添加底部
    def add_foot_widget(self, parent, config):

        def message_box_close(widget, text: str):
            config = self.load_config()
            
            # 生成一个随机 TAG
            tag = f"custom_platform_{random.randint(100000, 999999)}"

            # 修改和保存配置
            platform = copy.deepcopy(self.CUSTOM)
            platform["tag"] = tag
            platform["name"] = text.strip()
            config["platforms"][tag] = platform
            self.save_config(config)

            # 更新UI
            self.update_custom_platform_widgets(self.flow_card)

        def on_add_button_clicked(widget):
            message_box = LineEditMessageBox(
                self.window,
                "请输入新的接口名称 ...",
                message_box_close = message_box_close
            )
            
            message_box.exec()

        def init(widget):
            # 添加新增按钮
            add_button = PrimaryPushButton("新增")
            add_button.setIcon(FluentIcon.ADD_TO)
            add_button.setContentsMargins(4, 0, 4, 0)
            add_button.clicked.connect(lambda: on_add_button_clicked(self))
            widget.add_widget_to_head(add_button)

            # 更新控件
            self.update_custom_platform_widgets(widget)

        self.flow_card = FlowCard(
            "自定义接口", 
            "在此添加和管理任何符合 OpenAI 格式或者 Anthropic 格式的大语言模型的接口信息",
            init = init,
        )
        parent.addWidget(self.flow_card)